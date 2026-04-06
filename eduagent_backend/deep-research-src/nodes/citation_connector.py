"""Citation Connector Agent — A8.

Runs after all research iterations complete, before final_report_generation.

Steps:
  1. KG check    — for each top paper, query Neo4j: in corpus? → pull CCM η score
  2. Run Graph   — fetch L2/L3 citations from S2 for each top paper; grow the ancestry network
  3. Gap analysis — field anchors, chain termination gaps, thin chains, hypothesis surfaces
  4. Output      — run_graph_analysis dict → formatted into final report prompt

Fails silently at every step — the report still generates without this data.
"""

import asyncio
import logging
import os
import re
from typing import Optional

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from state import AgentState
from utils.ranking import rank_profiles
from utils.llm import get_today_str
from utils import run_logger

log = logging.getLogger(__name__)

_S2_BASE = "https://api.semanticscholar.org/graph/v1"
_S2_REF_FIELDS = "title,year,externalIds,intents,isInfluential"
_S2_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
_HEADERS = {"User-Agent": "EduResearchAgent/2.0 (academic research tool)"}
if _S2_KEY:
    _HEADERS["x-api-key"] = _S2_KEY

_INTENT_TO_LEVEL: dict[str, int] = {
    "background": 2,   # grounded → L2
    "methodology": 3,  # foundational → L3
    "result": 1,       # referential → L1
}

_MIN_YEAR_KG = 2023
_TOP_N = 30       # traverse S2 for top 30 ranked papers (matches max_sources)
_SLEEP = 2.0 if _S2_KEY else 5.0   # 2s with API key, 5s anonymous
_ETA_THRESHOLD = 0.50               # top ~20% of corpus η range (0.42–0.58)


# ── Main node ────────────────────────────────────────────────────────────────

async def citation_connector(state: AgentState, config: RunnableConfig) -> dict:
    """Build Run Graph, surface gaps and hypotheses, write architecture section."""
    configurable = Configuration.from_runnable_config(config)
    sid = configurable.session_id
    paper_profiles = state.get("paper_profiles", [])
    tqm = state.get("tiered_question_map") or {}
    research_brief = state.get("research_brief", "")

    if not paper_profiles:
        log.info("[citation_connector] No paper profiles — skipping.")
        return {"run_graph_analysis": {}, "run_graph_section": ""}

    ranked = rank_profiles(paper_profiles, research_brief, tqm)
    # Deduplicate by DOI then title before slicing — same paper can appear from multiple researchers
    seen_keys: set[str] = set()
    deduped = []
    for p in ranked:
        key = (_get(p, "doi") or (_get(p, "title") or "").lower()[:80]).strip()
        if key and key not in seen_keys:
            seen_keys.add(key)
            deduped.append(p)
    top_papers = deduped[:_TOP_N]

    run_logger.log(f"[citation_connector] Starting — {len(paper_profiles)} profiles, top {len(top_papers)} selected", sid)

    # Step 1 — KG check: pull CCM η scores for corpus papers
    run_logger.log("[citation_connector] Step 1: KG score lookup (CCM η, cluster_id, field_momentum)", sid)
    kg_scores = _check_kg_scores(top_papers)
    if kg_scores:
        log.info(f"[citation_connector] KG scores found for {len(kg_scores)} papers")

    # Step 2 — Build Run Graph via S2 traversal
    run_logger.log(f"[citation_connector] Step 2: Building Run Graph via S2 ({len(top_papers)} seed papers)", sid)
    run_graph: dict = {}
    try:
        run_graph = await _build_run_graph(top_papers, sid)
        log.info(f"[citation_connector] Run Graph: {len(run_graph)} nodes")
    except Exception as e:
        log.warning(f"[citation_connector] Run Graph build failed: {e}")

    # Step 3 — Gap analysis on Run Graph structure
    run_logger.log(f"[citation_connector] Step 3: Gap analysis ({len(run_graph)} run graph nodes)", sid)
    try:
        analysis = _analyze_run_graph(run_graph, kg_scores, top_papers)
    except Exception as e:
        run_logger.log(f"[citation_connector] Gap analysis failed: {e}", sid)
        log.warning(f"[citation_connector] _analyze_run_graph failed: {e}")
        analysis = {"anchors": [], "lineage": "", "lineage_chains": [], "gaps": [], "hypotheses": [], "high_eta": []}

    new_queued = sum(1 for n in run_graph.values() if n.get("status") == "new_2023")

    run_graph_analysis = {
        "field_anchors":        analysis["anchors"],
        "intellectual_lineage": analysis["lineage"],
        "lineage_chains":       analysis["lineage_chains"],
        "gaps":                 analysis["gaps"],
        "hypothesis_surfaces":  analysis["hypotheses"],
        "high_eta_confirmed":   analysis["high_eta"],
        "new_papers_queued":    new_queued,
        "run_graph_size":       len(run_graph),
    }

    log.info(
        f"[citation_connector] Analysis — {len(analysis['anchors'])} anchors, "
        f"{len(analysis['gaps'])} gaps, {len(analysis['hypotheses'])} hypotheses"
    )

    # Step 4 — Dedicated LLM call to write the architecture section as prose
    run_logger.log(f"[citation_connector] Step 4: Writing architecture section ({len(analysis['anchors'])} anchors, {len(analysis['gaps'])} gaps, {len(analysis['hypotheses'])} hypotheses)", sid)
    run_graph_section = ""
    if any([analysis["anchors"], analysis["gaps"], analysis["hypotheses"]]):
        try:
            run_graph_section = await _write_architecture_section(
                run_graph_analysis, research_brief, config, top_papers
            )
            run_logger.log("[citation_connector] Done — architecture section written", sid)
        except Exception as e:
            run_logger.log(f"[citation_connector] Architecture section failed: {e}", sid)
            log.warning(f"[citation_connector] Architecture section LLM call failed: {e}")

    return {
        "run_graph_analysis": run_graph_analysis,
        "run_graph_section":  run_graph_section,
    }


# ── Step 4: Write architecture section ───────────────────────────────────────

_ARCHITECTURE_SYSTEM = """You are a research synthesis specialist writing one section of an academic report.

Your task: write the "Research Architecture & Open Questions" section based on citation network data provided.

RULES:
- Write in plain academic prose paragraphs. No bullet lists.
- Do NOT invent statistics, paper titles, or author names beyond what is provided.
- If data is thin (few anchors, few gaps), be honest — do not pad with speculation.
- Do NOT use self-referential language ("this section", "as noted above").
- Be specific and concrete. Vague generalities are worse than silence.
- Length: 300–500 words total across all four subsections.
- CITATIONS: A numbered source pool is provided. Whenever you reference a paper from the pool, cite it inline using [N]. Do not cite papers not in the pool.

OUTPUT — write exactly these four subsections, in this order:

### Field Anchors
Which pre-2023 foundational works does this body of research build on? What did each establish that later work depends on methodologically or theoretically?

### Intellectual Lineage
Render this as a markdown table with columns: Foundational Paper | Year | What It Established | Extended By (papers from this run that build on it).
Use the Lineage Chains data provided. If no chains are available, write 2–3 prose sentences instead.

### Research Gaps
What does the citation structure reveal about where research has not yet gone? Name the specific populations, methodologies, or outcome types that appear to have no modern extensions.

### Hypothesis Surfaces
Based on the lineage, gaps, and what the source pool actually contains (study designs, populations, outcome measures), articulate 2–3 specific, testable research hypotheses.

IMPORTANT: The citation network analysis may include structural signals tagged ANCHOR_SIGNAL, CONVERGENCE_SIGNAL, MOMENTUM_SIGNAL, HIGH_ETA_SIGNAL. Use these as pointers to where gaps exist — but derive the actual hypothesis from the source pool evidence (what populations were studied, what designs were used, what outcomes were measured, what is conspicuously absent). Do NOT copy the signal text into the output. Each hypothesis must name: the specific population, the specific intervention type (grounded in what the source pool describes), the specific outcome measure, and the appropriate study design."""

_ARCHITECTURE_HUMAN = """Research brief: {research_brief}

Numbered source pool (use [N] to cite these inline):
{source_pool}

Citation network analysis:
{analysis_block}

Write the Research Architecture & Open Questions section now."""


_ARCHITECTURE_MODEL = "openai:gpt-5.4-2026-03-05"


async def _write_architecture_section(
    rga: dict, research_brief: str, config, top_papers: list = None
) -> str:
    """Call GPT 5.4 to write the architecture section prose from structured analysis data."""
    from langchain.chat_models import init_chat_model

    model = init_chat_model(model=_ARCHITECTURE_MODEL, max_tokens=1500)

    analysis_block = format_run_graph_analysis(rga)
    if not analysis_block:
        return ""

    # Build an enriched numbered source pool so LLM can reason about what evidence exists
    source_lines = []
    for i, p in enumerate(top_papers or [], 1):
        title = (_get(p, "title") or "")[:80]
        year = _get(p, "year") or "n.d."
        design = _get(p, "study_design") or "not_reported"
        pops = _get(p, "populations") or []
        pop_str = ", ".join(pops[:2]) if pops else "not_reported"
        summary = (_get(p, "extended_summary") or "")[:120]
        line = f"[{i}] ({year}) {title} | Design: {design} | Population: {pop_str}"
        if summary:
            line += f" | {summary}"
        source_lines.append(line)
    source_pool = "\n".join(source_lines) if source_lines else "No numbered sources available."

    human = _ARCHITECTURE_HUMAN.format(
        research_brief=research_brief[:500],
        source_pool=source_pool,
        analysis_block=analysis_block,
    )

    response = await model.ainvoke([
        SystemMessage(content=_ARCHITECTURE_SYSTEM),
        HumanMessage(content=human),
    ])

    prose = str(response.content).strip()
    if not prose:
        return ""

    # Strip any leading title the LLM may have emitted (we add our own)
    prose = re.sub(r'^#{1,3}\s*Research Architecture.*\n', '', prose, flags=re.IGNORECASE).strip()

    return f"## Research Architecture & Open Questions\n\n{prose}\n"


# ── Step 1: KG check ─────────────────────────────────────────────────────────

def _check_kg_scores(papers: list) -> dict:
    """Query Neo4j for CCM η scores of top papers. Returns {title_lower: scores_dict}."""
    if not os.environ.get("NEO4J_URI"):
        return {}

    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        titles = [(_get(p, "title") or "").lower() for p in papers if _get(p, "title")]

        with driver.session(database=database) as session:
            result = session.run(
                """
                MATCH (p:Paper)
                WHERE toLower(p.title) IN $titles
                RETURN p.title AS title,
                       p.eta AS eta,
                       p.cluster_id AS cluster_id,
                       p.field_momentum AS field_momentum,
                       p.sb_coef AS sb_coef,
                       p.is_sleeping_beauty AS is_sleeping_beauty
                """,
                titles=titles,
            )
            scores = {}
            for row in result:
                key = (row["title"] or "").lower()
                scores[key] = {
                    "eta":                row["eta"],
                    "cluster_id":         row["cluster_id"],
                    "field_momentum":     row["field_momentum"],
                    "sb_coef":            row["sb_coef"],
                    "is_sleeping_beauty": row["is_sleeping_beauty"],
                }
        driver.close()
        return scores
    except Exception as e:
        log.debug(f"[citation_connector] KG score check failed: {e}")
        return {}


# ── Step 2: Build Run Graph ───────────────────────────────────────────────────

async def _build_run_graph(papers: list, session_id: str = "") -> dict:
    """Fetch references for each top paper via S2. Build ancestry network.

    All refs are included (L1/L2/L3) — L2/L3 just accrue higher in-degree counts.
    """
    if not papers:
        return {}
    run_graph: dict = {}
    sem = asyncio.Semaphore(1)  # one S2 request at a time (anonymous limit)

    async with httpx.AsyncClient(timeout=30.0) as client:
        for paper in papers:
            doi   = _get(paper, "doi") or ""
            title = _get(paper, "title") or ""
            if not doi and not title:
                continue

            try:
                refs = await _fetch_s2_refs(client, sem, doi, title)
            except Exception as e:
                log.debug(f"[citation_connector] _fetch_s2_refs error for '{title[:50]}': {e}")
                continue

            refs = refs or []
            run_logger.log(f"[citation_connector] S2 refs for '{title[:50]}': {len(refs)} total", session_id)

            for ref in refs:

                ref_doi   = ref["doi"] or ""
                ref_title = ref["title"] or ""
                ref_year  = ref["year"] or 0
                key = (ref_doi or ref_title[:60]).lower()
                if not key:
                    continue

                if key not in run_graph:
                    if ref_year >= _MIN_YEAR_KG:
                        status = "new_2023"
                    else:
                        status = "pre_2023"
                    run_graph[key] = {
                        "title":        ref_title,
                        "year":         ref_year,
                        "doi":          ref_doi,
                        "status":       status,
                        "l3_in_degree": 0,
                        "l2_in_degree": 0,
                        "cited_by":     [],
                    }

                if ref["level"] == 3:
                    run_graph[key]["l3_in_degree"] += 1
                else:
                    run_graph[key]["l2_in_degree"] += 1

                if title and title[:80] not in run_graph[key]["cited_by"]:
                    run_graph[key]["cited_by"].append(title[:80])

    return run_graph


async def _fetch_s2_refs(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    doi: str,
    title: str,
) -> list[dict]:
    """Fetch L2/L3 references for one paper from S2. Returns list of ref dicts."""
    async with sem:
        raw: Optional[dict] = None

        # Try DOI first
        if doi:
            try:
                resp = await client.get(
                    f"{_S2_BASE}/paper/DOI:{doi}/references",
                    params={"fields": _S2_REF_FIELDS, "limit": 100},
                    headers=_HEADERS,
                )
                if resp.status_code == 200:
                    raw = resp.json()
                elif resp.status_code == 429:
                    log.warning("[citation_connector] S2 rate limited — skipping this paper")
                await asyncio.sleep(_SLEEP)
            except Exception as e:
                log.debug(f"[citation_connector] S2 DOI fetch error: {e}")

        # Title search fallback
        if raw is None and title:
            try:
                search = await client.get(
                    f"{_S2_BASE}/paper/search",
                    params={"query": title[:100], "fields": "externalIds", "limit": 1},
                    headers=_HEADERS,
                )
                await asyncio.sleep(_SLEEP)
                if search.status_code == 200:
                    hits = search.json().get("data", [])
                    if hits:
                        s2_id = hits[0].get("paperId", "")
                        if s2_id:
                            ref_resp = await client.get(
                                f"{_S2_BASE}/paper/{s2_id}/references",
                                params={"fields": _S2_REF_FIELDS, "limit": 100},
                                headers=_HEADERS,
                            )
                            await asyncio.sleep(_SLEEP)
                            if ref_resp.status_code == 200:
                                raw = ref_resp.json()
            except Exception as e:
                log.debug(f"[citation_connector] S2 title search error: {e}")

        if not raw:
            return []

        refs = []
        for item in raw.get("data", []):
            cited   = item.get("citedPaper") or {}
            intents = item.get("intents") or []
            level   = max((_INTENT_TO_LEVEL.get(i, 1) for i in intents), default=1)
            ext     = cited.get("externalIds") or {}
            refs.append({
                "title": cited.get("title") or "",
                "year":  cited.get("year") or 0,
                "doi":   ext.get("DOI") or "",
                "level": level,
            })
        return refs


# ── Step 3: Gap analysis ──────────────────────────────────────────────────────

def _analyze_run_graph(run_graph: dict, kg_scores: dict, top_papers: list) -> dict:
    """Surface field anchors, gaps, hypotheses from Run Graph + CCM scores."""

    # Field anchors: pre-2023 papers L3-cited by 2+ top papers
    anchors = sorted(
        [n for n in run_graph.values() if n["status"] == "pre_2023" and n["l3_in_degree"] >= 2],
        key=lambda n: -n["l3_in_degree"],
    )
    anchor_strs = [
        f"'{n['title'][:65]}' ({n['year']}) — L3-cited by {n['l3_in_degree']} papers in this run"
        for n in anchors[:5]
    ]

    # Thin chains: L3 ancestors cited by only 1 paper (underexplored)
    thin_count = sum(
        1 for n in run_graph.values()
        if n["status"] == "pre_2023" and n["l3_in_degree"] == 1
    )

    # High-η confirmed: run papers that are in corpus with strong CCM scores
    high_eta = []
    for p in top_papers:
        key = (_get(p, "title") or "").lower()
        s = kg_scores.get(key, {})
        eta = s.get("eta")
        if eta and eta >= _ETA_THRESHOLD:
            high_eta.append({
                "title":          _get(p, "title"),
                "eta":            round(eta, 2),
                "cluster_id":     s.get("cluster_id"),
                "field_momentum": s.get("field_momentum"),
            })

    # Chain termination gaps: corpus papers in run graph not extended via L3 by others
    gaps = []
    cluster_momentum: dict = {}   # populated below if kg_scores available
    for n in run_graph.values():
        if n["status"] == "new_2023" and n["l3_in_degree"] == 0:
            key = n["title"].lower()
            eta = kg_scores.get(key, {}).get("eta", 0) or 0
            if eta >= _ETA_THRESHOLD:
                gaps.append(
                    f"Chain termination: '{n['title'][:65]}' ({n['year']}) — high-η corpus paper "
                    f"(η={eta:.2f}) with no L3 extensions found in this run"
                )

    # Momentum gap: high field_momentum clusters with no RCT evidence in this run
    if kg_scores:
        cluster_momentum: dict[int, float] = {}
        cluster_designs:  dict[int, list]  = {}
        for p in top_papers:
            key = (_get(p, "title") or "").lower()
            s = kg_scores.get(key, {})
            cid = s.get("cluster_id")
            fm  = s.get("field_momentum")
            if cid is not None and fm is not None:
                cluster_momentum[cid] = max(cluster_momentum.get(cid, 0), fm)
                design = (_get(p, "study_design") or "").lower()
                cluster_designs.setdefault(cid, []).append(design)

        for cid, fm in cluster_momentum.items():
            if fm >= 0.60:
                designs = cluster_designs.get(cid, [])
                has_rct = any("rct" in d or "randomized" in d or "random" in d for d in designs)
                if not has_rct:
                    gaps.append(
                        f"Momentum gap: cluster {cid} has field_momentum={fm:.2f} "
                        f"(highly active sub-field) but no RCT-level evidence found in this run"
                    )

    # Structural proxy gaps when CCM scores unavailable
    if not kg_scores:
        if thin_count > 0:
            gaps.append(
                f"{thin_count} foundational pre-2023 paper(s) are L3-cited by only one run paper — "
                "potentially underexplored threads worth investigating"
            )
        for n in anchors[:2]:
            gaps.append(
                f"'{n['title'][:65]}' ({n['year']}) is a load-bearing anchor but coverage may be "
                "thin for specific populations or outcome types"
            )

    # Hypothesis signals — structural facts only, no templated text.
    # The LLM derives actual hypotheses from these signals + the source pool + research brief.
    hypotheses = []
    if anchors:
        hypotheses.append(
            f"ANCHOR_SIGNAL: '{anchors[0]['title'][:65]}' ({anchors[0]['year']}) "
            f"is L3-cited by {anchors[0]['l3_in_degree']} papers but may lack extensions "
            "for specific populations, outcome types, or AI modalities present in this run"
        )
    shared_l2 = [n for n in run_graph.values() if n["status"] == "new_2023" and n["l2_in_degree"] >= 2]
    if shared_l2:
        hypotheses.append(
            f"CONVERGENCE_SIGNAL: {len(shared_l2)} post-2023 papers share L2 conceptual grounding "
            "— multiple approaches are building on the same foundations without direct comparison"
        )
    if cluster_momentum:
        top_cid = max(cluster_momentum, key=lambda c: cluster_momentum[c])
        top_fm  = cluster_momentum[top_cid]
        if top_fm >= 0.60:
            hypotheses.append(
                f"MOMENTUM_SIGNAL: cluster {top_cid} has field_momentum={top_fm:.2f} "
                "(high active-building) but no RCT-level evidence found in this run"
            )
    if high_eta and not gaps:
        top = high_eta[0]
        hypotheses.append(
            f"HIGH_ETA_SIGNAL: '{top['title'][:65]}' (η={top['eta']}) is highly cited "
            "in the network but has no direct methodological extensions in this run"
        )

    # Intellectual lineage description
    if anchors:
        lineage = (
            f"This body of research builds on {len(anchors)} pre-2023 foundational work(s). "
            f"The most load-bearing anchor is '{anchors[0]['title'][:55]}' ({anchors[0]['year']}), "
            f"L3-cited by {anchors[0]['l3_in_degree']} of the top papers in this run. "
            f"The Run Graph spans {len(run_graph)} unique referenced works across the full ancestry."
        )
    elif run_graph:
        lineage = (
            f"The Run Graph spans {len(run_graph)} referenced works. "
            "No dominant pre-2023 foundational anchor was identified from available citation data — "
            "this may indicate an emerging field without consolidated theoretical roots."
        )
    else:
        lineage = "S2 citation data was unavailable for this run — citation architecture analysis not performed."

    # Build lineage chains: for each anchor, find which top papers cite it and what they build toward
    lineage_chains = []
    for anchor in anchors[:5]:
        anchor_title = anchor["title"]
        # cited_by contains the titles ([:80]) of top_papers that cited this anchor
        cited_by_set = {t.lower() for t in anchor.get("cited_by", [])}
        citing = [
            p for p in top_papers
            if (_get(p, "title") or "")[:80].lower() in cited_by_set
        ][:3]
        chain = {
            "anchor_title": anchor_title[:65],
            "anchor_year":  anchor["year"],
            "l3_count":     anchor["l3_in_degree"],
            "citing_papers": [
                {"title": (_get(p, "title") or "")[:65], "year": _get(p, "year") or "n.d."}
                for p in citing
            ] if citing else [
                {"title": t[:65], "year": ""} for t in anchor.get("cited_by", [])[:3]
            ],
        }
        lineage_chains.append(chain)

    return {
        "anchors":        anchor_strs,
        "lineage":        lineage,
        "lineage_chains": lineage_chains,
        "gaps":           gaps[:6],
        "hypotheses":     hypotheses[:4],
        "high_eta":       [f"{p['title'][:60]} (η={p['eta']}, cluster={p['cluster_id']}, fm={p['field_momentum']})" for p in high_eta[:5]],
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# ── Public formatter (used by nodes/report.py) ────────────────────────────────

def format_run_graph_analysis(rga: dict) -> str:
    """Format run_graph_analysis dict into a prompt block for the final report LLM."""
    if not rga:
        return ""

    anchors    = rga.get("field_anchors") or []
    lineage    = rga.get("intellectual_lineage") or ""
    chains     = rga.get("lineage_chains") or []
    gaps       = rga.get("gaps") or []
    hypotheses = rga.get("hypothesis_surfaces") or []
    high_eta   = rga.get("high_eta_confirmed") or []
    new_queued = rga.get("new_papers_queued", 0)
    graph_size = rga.get("run_graph_size", 0)

    if not any([anchors, gaps, hypotheses, lineage]):
        return ""

    lines = [
        "## Citation Architecture Data",
        f"(Run Graph: {graph_size} referenced works | {new_queued} new papers queued for KG ingest)",
        "",
    ]
    if lineage:
        lines += ["Intellectual Lineage:", lineage, ""]
    if chains:
        lines += ["Lineage Chains (foundational paper → papers that build on it):"]
        for ch in chains:
            citing_titles = " | ".join(
                f"{p['title'][:50]} ({p['year']})" if p['year'] else p['title'][:50]
                for p in ch["citing_papers"]
            ) or "no citing papers identified"
            lines.append(
                f"  Anchor: '{ch['anchor_title']}' ({ch['anchor_year']}, L3-cited by {ch['l3_count']} papers)"
                f" → built on by: {citing_titles}"
            )
        lines.append("")
    if anchors:
        lines += ["Field Anchors (pre-2023 load-bearing foundations):"]
        lines += [f"  - {a}" for a in anchors]
        lines.append("")
    if high_eta:
        lines += ["High-impact papers confirmed in this run (CCM η score):"]
        lines += [f"  - {e}" for e in high_eta]
        lines.append("")
    if gaps:
        lines += ["Research Gaps Identified:"]
        lines += [f"  - {g}" for g in gaps]
        lines.append("")
    if hypotheses:
        lines += ["Hypothesis Surfaces (open experimental slots):"]
        lines += [f"  - {h}" for h in hypotheses]
        lines.append("")

    return "\n".join(lines)

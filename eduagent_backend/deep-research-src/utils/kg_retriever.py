"""KG retriever — queries Neo4j corpus for papers relevant to a research brief.

Called by education_discovery before researchers are dispatched. Returns
PaperProfile-compatible dicts that are added directly to paper_profiles in
AgentState so they compete freely with researcher-found papers for the top-k
source pool in the final report.

Papers that make the top-k get cited in the report — completing the full circle:
  weekly batch → Neo4j → A7 retrieval → paper_profiles → rank_profiles → report
"""

import logging
import os
import re

from utils import run_logger

log = logging.getLogger(__name__)

_QUALITY_ORDER = {"blue": 0, "green": 1, "yellow": 2, "red": 99}
_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "for", "to", "with",
    "how", "what", "does", "is", "are", "do", "use", "using", "used", "impact",
    "effect", "effects", "learning", "education", "students", "study", "research",
}


# ── Public API ──────────────────────────────────────────────────────────────────

def query_kg_for_topic(
    focal_intervention: str,
    population: str,
    topic_keywords: list[str],
    top_k: int = 20,
    session_id: str = "",
) -> list[dict]:
    """Query Neo4j for corpus papers relevant to the research brief.

    Returns a list of paper dicts compatible with report.py's source pool
    (same fields as PaperProfile). Returns [] if Neo4j is unavailable or
    no relevant papers are found — never raises.

    Args:
        focal_intervention: e.g. "ChatGPT for essay feedback"
        population: e.g. "high school students"
        topic_keywords: additional keywords from the research topic/brief
        top_k: maximum papers to return
    """
    if not os.environ.get("NEO4J_URI"):
        log.debug("[kg_retriever] NEO4J_URI not set — skipping KG lookup.")
        return []

    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
    except Exception as e:
        log.warning(f"[kg_retriever] Neo4j connection failed: {e}")
        return []

    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    results: list[dict] = []

    try:
        with driver.session(database=database) as session:
            # Extract clean keyword lists for matching
            intervention_kws = _extract_keywords(focal_intervention)
            pop_kw = _extract_pop_keyword(population)
            broad_kws = list(set(
                intervention_kws
                + _extract_keywords(" ".join(topic_keywords))
            ))[:8]  # cap to avoid giant CONTAINS chains

            # Query 1: papers linked to matching Intervention nodes (highest signal)
            intervention_papers = _query_by_intervention(session, intervention_kws)

            # Query 2: papers matching keywords in title/summary + population
            keyword_papers = _query_by_keywords(session, broad_kws, pop_kw)

            results = _merge_and_rank(intervention_papers, keyword_papers, top_k)

    except Exception as e:
        log.warning(f"[kg_retriever] Query error: {e}")
    finally:
        driver.close()

    run_logger.log(f"[kg_retriever] Retrieved {len(results)} relevant KG papers", session_id)
    return results


def format_kg_evidence_block(papers: list[dict]) -> str:
    """Format KG papers into a supervisor context block.

    Tells researchers what the KG already knows so they focus on gaps.
    """
    if not papers:
        return ""

    lines = [
        "## KG Evidence Base — papers already in corpus",
        f"({len(papers)} papers retrieved — these are already known. Focus research on gaps and populations not covered below.)\n",
    ]

    for i, p in enumerate(papers, 1):
        title = p.get("title", "Unknown")
        year = p.get("year") or "n.d."
        quality = p.get("quality_tier", "yellow")
        impact = p.get("impact_tier", "yellow")
        design = p.get("study_design", "not_reported")
        pops = p.get("populations") or []
        pop_str = ", ".join(pops[:2]) if pops else "not_reported"
        url = p.get("url") or p.get("doi") or ""

        header = f"[KG{i}] ({year}) {title}"
        if url:
            header += f" — {url}"
        meta = f"    Quality: {quality} | Impact: {impact} | Design: {design} | Population: {pop_str}"

        lines.append(header)
        lines.append(meta)

        # Include top finding if available
        for oa in (p.get("outcome_assignments") or [])[:1]:
            finding = oa.get("finding") or {}
            summary = (finding.get("finding_summary") or "")[:180]
            effect = finding.get("effect_size", "")
            n = finding.get("study_size", "")
            if summary:
                stat = f"    Finding: {summary}"
                if effect and effect != "not_reported":
                    stat += f" [{effect}]"
                if n and n != "not_reported":
                    stat += f" [n={n.lstrip('n=').lstrip('N=')}]"
                lines.append(stat)

        lines.append("")

    return "\n".join(lines)


# ── Neo4j queries ───────────────────────────────────────────────────────────────

def _query_by_intervention(session, intervention_kws: list[str]) -> list[dict]:
    """Papers linked via EVALUATES to an Intervention whose name matches keywords."""
    if not intervention_kws:
        return []

    # Build WHERE clause: any keyword appears in intervention name
    conditions = " OR ".join(
        f"toLower(i.name) CONTAINS $kw{idx}"
        for idx in range(len(intervention_kws))
    )
    params = {f"kw{idx}": kw for idx, kw in enumerate(intervention_kws)}
    params["limit"] = 40

    result = session.run(f"""
        MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
        WHERE ({conditions})
          AND p.quality_tier <> 'red'
        OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
        WITH p, collect(DISTINCT i.name) AS interventions,
             collect(f)[0..3] AS findings
        RETURN p, interventions, findings
        LIMIT $limit
    """, params)

    return [_row_to_paper(r) for r in result]


def _query_by_keywords(session, keywords: list[str], pop_kw: str) -> list[dict]:
    """Papers matching keywords in title/summary or population."""
    if not keywords and not pop_kw:
        return []

    kw_conditions = " OR ".join(
        f"toLower(p.title) CONTAINS $kw{idx} OR toLower(p.extended_summary) CONTAINS $kw{idx}"
        for idx in range(len(keywords))
    )
    pop_condition = "any(pop IN p.populations WHERE toLower(pop) CONTAINS $pop_kw)" if pop_kw else ""

    conditions_parts = [c for c in [kw_conditions, pop_condition] if c]
    if not conditions_parts:
        return []
    conditions = " OR ".join(f"({c})" for c in conditions_parts)

    params = {f"kw{idx}": kw for idx, kw in enumerate(keywords)}
    if pop_kw:
        params["pop_kw"] = pop_kw
    params["limit"] = 40

    result = session.run(f"""
        MATCH (p:Paper)
        WHERE p.quality_tier <> 'red'
          AND ({conditions})
        OPTIONAL MATCH (p)-[:EVALUATES]->(i:Intervention)
        OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
        WITH p, collect(DISTINCT i.name) AS interventions,
             collect(f)[0..3] AS findings
        RETURN p, interventions, findings
        LIMIT $limit
    """, params)

    return [_row_to_paper(r) for r in result]


# ── Row → paper dict ────────────────────────────────────────────────────────────

def _row_to_paper(row) -> dict:
    """Convert a Neo4j result row to a PaperProfile-compatible dict."""
    p = dict(row["p"])
    interventions = row["interventions"] or []
    findings = row["findings"] or []

    # Build identified_tools: group findings by the intervention they were produced by
    # (interventions list from Neo4j is just names; findings are EmpiricalFinding nodes)
    kg_findings = []
    for f in findings:
        fd = dict(f)
        kg_findings.append({
            "outcome_category":   fd.get("outcome_category", ""),
            "finding_type":       fd.get("finding_type", "primary"),
            "direction":          fd.get("direction", ""),
            "finding_summary":    fd.get("finding_summary", ""),
            "measure":            fd.get("measure", "not_reported"),
            "sample_size":        fd.get("sample_size", "not_reported"),
            "effect_size":        fd.get("effect_size", "not_reported"),
            "confidence_interval":fd.get("confidence_interval", "not_reported"),
        })

    identified_tools = []
    for name in (interventions or []):
        identified_tools.append({
            "name":             name,
            "is_named_product": True,
            "specificity":      "named_tool",
            "category_key":     [],
            "description":      "",
            "use_case":         "",
            "findings":         kg_findings,
        })

    return {
        "title":              p.get("title", ""),
        "doi":                p.get("doi"),
        "year":               p.get("year"),
        "venue":              p.get("venue", ""),
        "url":                p.get("url", ""),
        "source_db":          p.get("source_db", "kg_corpus"),
        "populations":        p.get("populations") or [],
        "user_types":         p.get("user_types") or [],
        "study_design":       p.get("study_design", "not_reported"),
        "extended_summary":   p.get("extended_summary", ""),
        "quality_tier":       p.get("quality_tier", "yellow"),
        "impact_tier":        p.get("impact_tier", "yellow"),
        "limitations":        p.get("limitations") or [],
        "duration_weeks":     p.get("duration_weeks", "not_reported"),
        "setting":            p.get("setting", "not_reported"),
        "teacher_training":   p.get("teacher_training", "not_reported"),
        "implementation_fidelity": p.get("implementation_fidelity", "not_reported"),
        "study_country":      p.get("study_country", "not_reported"),
        "study_region":       p.get("study_region", "not_reported"),
        "extraction_status":  "full_text",
        "extraction_note":    "Retrieved from KG corpus",
        "identified_tools":   identified_tools,
        "verdict":            "named_tool_found" if identified_tools else "no_tool",
        "authors":            "",   # not stored in Neo4j — title used in bibliography
        "_kg_source":         True,
    }


# ── Merge + rank ────────────────────────────────────────────────────────────────

def _merge_and_rank(
    intervention_papers: list[dict],
    keyword_papers: list[dict],
    top_k: int,
) -> list[dict]:
    """Deduplicate by title (lowercase) and rank: intervention match first,
    then by quality tier (blue→green→yellow), then year descending."""
    seen: set[str] = set()
    merged: list[tuple[int, dict]] = []  # (priority, paper)

    for p in intervention_papers:
        key = (p.get("title") or "").lower().strip()[:80]
        if key and key not in seen:
            seen.add(key)
            merged.append((0, p))  # priority 0 = intervention match

    for p in keyword_papers:
        key = (p.get("title") or "").lower().strip()[:80]
        if key and key not in seen:
            seen.add(key)
            merged.append((1, p))  # priority 1 = keyword match

    merged.sort(key=lambda x: (
        x[0],                                            # intervention match first
        _QUALITY_ORDER.get(x[1].get("quality_tier", "yellow"), 2),
        -(x[1].get("year") or 0),                        # newer first
    ))

    return [p for _, p in merged[:top_k]]


# ── Keyword helpers ─────────────────────────────────────────────────────────────

def _extract_keywords(text: str) -> list[str]:
    """Extract significant lowercase words from text, filtered by stopwords."""
    words = re.findall(r"[a-z]{3,}", text.lower())
    return [w for w in words if w not in _STOPWORDS][:6]


def _extract_pop_keyword(population: str) -> str:
    """Extract a single population keyword for matching."""
    pop = population.lower()
    if "high school" in pop or "secondary" in pop:
        return "high school"
    if "middle school" in pop or "middle" in pop:
        return "middle school"
    if "elementary" in pop or "primary" in pop or "k-5" in pop:
        return "elementary"
    if "undergraduate" in pop or "college" in pop or "university" in pop:
        return "undergraduate"
    if "graduate" in pop or "doctoral" in pop:
        return "graduate"
    if "k-12" in pop or "k12" in pop:
        return "k-12"
    return ""

"""Final report node — writes definitive report directly from paper profiles."""

import re
import logging
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import final_report_prompt, citation_normalize_prompt
from state import AgentState, PaperProfile
from utils.llm import get_model, get_today_str
from utils.citations import inject_citations as _inject_citations, build_notes_index
from utils.ranking import rank_profiles

logger = logging.getLogger(__name__)


def _build_paper_tier_reference(profiles: list[PaperProfile], numbered: bool = False) -> tuple[str, dict[int, dict]]:
    """
    Format PaperProfiles into a source list for report prompts.
    Returns (formatted_block, index_map) where index_map maps [N] → profile dict.
    When numbered=True, each entry is prefixed with [N] for Pass 2 citation resolution.
    """
    if not profiles:
        return "No pre-scored profiles available.", {}

    seen_dois: set[str] = set()
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    deduped = []
    for p in profiles:
        if isinstance(p, dict):
            doi = (p.get("doi") or "").strip().lower()
            url = (p.get("url") or "").strip().lower()
            title = (p.get("title") or "").strip().lower()
        else:
            doi = (getattr(p, "doi", None) or "").strip().lower()
            url = (getattr(p, "url", None) or "").strip().lower()
            title = (getattr(p, "title", None) or "").strip().lower()

        if doi and doi in seen_dois:
            continue
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue

        if doi:
            seen_dois.add(doi)
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        deduped.append(p)

    lines = []
    index_map: dict[int, dict] = {}

    for i, p in enumerate(deduped, start=1):
        if isinstance(p, dict):
            title = p.get("title", "Unknown")
            authors = p.get("authors") or ""
            doi = p.get("doi") or ""
            year = p.get("year") or "n.d."
            url = p.get("url") or doi or "not available"
            quality = p.get("quality_tier", "yellow")
            impact = p.get("impact_tier", "yellow")
            study_design = p.get("study_design", "not_reported")
            population = p.get("population", "not_reported")
            extended_summary = (p.get("extended_summary") or "")[:300]
            outcome_assignments = p.get("outcome_assignments") or []
        else:
            title = getattr(p, "title", "Unknown")
            authors = getattr(p, "authors", None) or ""
            doi = getattr(p, "doi", None) or ""
            year = getattr(p, "year", None) or "n.d."
            url = getattr(p, "url", None) or doi or "not available"
            quality = getattr(p, "quality_tier", "yellow")
            impact = getattr(p, "impact_tier", "yellow")
            study_design = getattr(p, "study_design", "not_reported")
            population = getattr(p, "population", "not_reported")
            extended_summary = (getattr(p, "extended_summary", "") or "")[:300]
            outcome_assignments = getattr(p, "outcome_assignments", None) or []

        index_map[i] = {
            "title": title, "authors": authors, "year": year,
            "url": url, "study_design": study_design,
            "quality": quality, "impact": impact,
        }

        _CAUSAL_DESIGNS = {"Randomized Controlled Trial (RCT)", "RCT",
                           "Quasi-Experimental Design (QED)", "QED",
                           "Meta-Analysis", "Systematic Review"}
        stats_lines = []
        if study_design in _CAUSAL_DESIGNS and outcome_assignments:
            for oa in outcome_assignments:
                if isinstance(oa, dict):
                    outcome = oa.get("outcome", "")
                    finding = oa.get("finding") or {}
                    summary = (finding.get("finding_summary") or "")[:200]
                    effect = finding.get("effect_size", "not_reported")
                    n = finding.get("study_size", "not_reported")
                    ci = finding.get("confidence_interval", "not_reported")
                else:
                    outcome = getattr(oa, "outcome", "")
                    f = getattr(oa, "finding", None)
                    summary = (getattr(f, "finding_summary", "") or "")[:200] if f else ""
                    effect = getattr(f, "effect_size", "not_reported") if f else "not_reported"
                    n = getattr(f, "study_size", "not_reported") if f else "not_reported"
                    ci = getattr(f, "confidence_interval", "not_reported") if f else "not_reported"
                if summary:
                    stat_str = f"    Finding [{outcome}]: {summary}"
                    if effect != "not_reported":
                        stat_str += f" | effect={effect}"
                    if n != "not_reported":
                        n_clean = n.lstrip("n=").lstrip("N=") if n.lower().startswith("n=") else n
                        stat_str += f" | n={n_clean}"
                    if ci != "not_reported":
                        stat_str += f" | CI={ci}"
                    stats_lines.append(stat_str)

        prefix = f"[{i}] " if numbered else ""
        entry = (
            f"{prefix}{authors} ({year}). {title}\n"
            f"    URL: {url}\n"
            f"    Design: {study_design} | Population: {population}\n"
            f"    Quality: {quality} | Impact: {impact}\n"
            f"    Summary: {extended_summary}"
        )
        if stats_lines:
            entry += "\n" + "\n".join(stats_lines)
        lines.append(entry)

    return "\n\n".join(lines), index_map


def _build_tiered_questions(tqm: dict) -> str:
    """Format the tiered question map into a readable block."""
    if not tqm:
        return "No tiered questions available."

    tier_labels = {
        "tier1": "Tier 1 — Foundational Framing",
        "tier2": "Tier 2 — Baseline and Existing Approaches",
        "tier3": "Tier 3 — Mechanisms and Implementation",
        "tier4": "Tier 4 — Comparative Evidence and Implications",
    }

    lines = []
    for key, label in tier_labels.items():
        questions = tqm.get(key, [])
        if questions:
            lines.append(f"{label}:")
            for q in questions:
                lines.append(f"  - {q}")

    return "\n".join(lines) if lines else "No tiered questions available."


def _build_bibliography(cited_ns: list[int], index_map: dict[int, dict]) -> str:
    """Programmatically build the bibliography table from injected [N] numbers."""
    if not cited_ns:
        return "No sources cited.\n"

    rows = []
    for n in sorted(cited_ns):
        profile = index_map.get(n)
        if not profile:
            continue
        title = profile.get("title", "Unknown")
        authors = profile.get("authors") or ""
        year = profile.get("year") or "n.d."
        url = profile.get("url") or ""
        design = profile.get("study_design", "not_reported")
        quality = (profile.get("quality") or "yellow").capitalize()
        impact = (profile.get("impact") or "yellow").capitalize()

        if url and url != "not available":
            citation = f"{authors} ({year}). [{title}]({url})."
        else:
            citation = f"{authors} ({year}). {title}."

        rows.append(f"| {n} | {citation} | {design} | {quality} | {impact} |")

    if not rows:
        return "No sources cited.\n"

    header = (
        "| # | Citation | Study Design | Quality | Impact |\n"
        "|---|----------|--------------|---------|--------|\n"
    )
    return header + "\n".join(rows) + "\n"


def _post_process_report(raw: str, index_map: dict[int, dict]) -> str:
    """
    Post-process the LLM-generated report:
    1. Inject [N] citations from (Author, Year) patterns
    2. Split off the Bibliography section (if present) and rebuild it programmatically
    3. Preserve the Body of Evidence Maturity section
    """
    # Split into body / bibliography / maturity
    bib_pattern = re.compile(r'^## Bibliography', re.MULTILINE)
    maturity_pattern = re.compile(r'^## Body of Evidence Maturity', re.MULTILINE)

    bib_match = bib_pattern.search(raw)
    maturity_match = maturity_pattern.search(raw)

    if bib_match:
        body = raw[:bib_match.start()]
        rest = raw[bib_match.start():]
    elif maturity_match:
        body = raw[:maturity_match.start()]
        rest = raw[maturity_match.start():]
    else:
        body = raw
        rest = ""

    # Preserve maturity section from rest
    if maturity_match and bib_match:
        # maturity is after bibliography
        maturity_start = maturity_pattern.search(rest)
        maturity_section = rest[maturity_start.start():] if maturity_start else ""
    elif maturity_match and not bib_match:
        maturity_section = rest
    else:
        maturity_section = ""

    # Strip any unresolved <<...>> tags left by Pass 2 (convert to plain text)
    body = re.sub(r'<<([^>]+)>>', r'(\1)', body)

    # Inject [N] into body (catches any remaining (Author, Year) refs)
    annotated_body = _inject_citations(body, index_map)

    # Collect all cited [N]
    cited_ns = list(set(int(m.group(1)) for m in re.finditer(r'\[(\d+)\]', annotated_body)))

    injected = len(cited_ns)
    logger.info(f"[final_report] {injected} unique [N] citations injected programmatically")

    # Build bibliography
    bibliography = "## Bibliography\n\n" + _build_bibliography(cited_ns, index_map)

    # Reassemble
    parts = [annotated_body.rstrip(), "", bibliography]
    if maturity_section:
        parts.append(maturity_section.strip())

    return "\n".join(parts)


async def final_report(state: AgentState, config: RunnableConfig) -> dict:
    """Write the final report directly from paper profiles and executive summaries."""
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config)

    paper_profiles = state.get("paper_profiles", [])
    critique_history = state.get("critique_history", [])
    all_notes = state.get("all_notes", [])
    tqm = state.get("tiered_question_map") or {}

    ranked_profiles = rank_profiles(paper_profiles, state.get("research_brief", ""), tqm)
    pool_size = configurable.max_sources * 2
    top_profiles = ranked_profiles[:pool_size]
    logger.info(f"[final_report] Source pool: {len(top_profiles)} of {len(ranked_profiles)} ranked profiles (max_sources={configurable.max_sources})")

    # Pass 1 pool: unlabelled (no [N]) so LLM writes <<Author, Year>> naturally
    paper_tier_reference, index_map = _build_paper_tier_reference(top_profiles, numbered=False)
    # Pass 2 pool: numbered with [N] so resolver can map <<...>> → [N] directly
    numbered_tier_reference, _ = _build_paper_tier_reference(top_profiles, numbered=True)
    tiered_questions = _build_tiered_questions(tqm)

    critique_summaries = "\n\n---\n\n".join(critique_history) if critique_history else "No critiques conducted."

    prompt = final_report_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        paper_tier_reference=paper_tier_reference,
        critique_summaries=critique_summaries,
        tiered_questions=tiered_questions,
        max_sources=configurable.max_sources,
    )

    # Pass 1 — content generation (LLM uses <<Author, Year>> tags)
    response = await model.ainvoke([HumanMessage(content=prompt)])
    raw_content = str(response.content)
    logger.info("[final_report] Pass 1 complete — resolving <<...>> citation tags")

    # Pass 2 — resolve <<...>> tags → [N] using numbered source pool
    normalize_prompt = citation_normalize_prompt.format(
        paper_tier_reference=numbered_tier_reference,
        report=raw_content,
    )
    norm_response = await model.ainvoke([HumanMessage(content=normalize_prompt)])
    normalized_content = str(norm_response.content)
    logger.info("[final_report] Pass 2 complete — citation tags resolved")

    # Augment index_map with notes-sourced papers
    notes_index = build_notes_index(all_notes, [], index_map)
    full_index_map = {**index_map, **notes_index}

    # Post-process: inject any remaining (Author, Year) refs and rebuild bibliography
    content = _post_process_report(normalized_content, full_index_map)

    return {
        "final_report": content,
        "messages": [AIMessage(content=content)],
    }

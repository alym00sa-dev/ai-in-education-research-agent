"""Final report node — reconciles all iteration drafts into the definitive report."""

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import final_report_prompt
from state import AgentState, PaperProfile
from utils.llm import get_model, get_today_str


def _build_paper_tier_reference(profiles: list[PaperProfile]) -> tuple[str, dict[int, dict]]:
    """
    Format PaperProfiles into a pre-numbered source list for the final report prompt.
    Returns (formatted_block, index_map) where index_map maps [N] → profile dict.
    """
    if not profiles:
        return "No pre-scored profiles available.", {}

    # Deduplicate: prefer DOI, fall back to normalised title
    seen_keys: set[str] = set()
    deduped = []
    for p in profiles:
        if isinstance(p, dict):
            doi = (p.get("doi") or "").strip().lower()
            title = (p.get("title") or "").strip().lower()
        else:
            doi = (getattr(p, "doi", None) or "").strip().lower()
            title = (getattr(p, "title", None) or "").strip().lower()
        key = doi if doi else title
        if key and key not in seen_keys:
            seen_keys.add(key)
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

        index_map[i] = {
            "title": title, "authors": authors, "year": year,
            "url": url, "study_design": study_design,
            "quality": quality, "impact": impact,
        }

        lines.append(
            f"[{i}] {title} ({year}). {authors}\n"
            f"    URL: {url}\n"
            f"    Design: {study_design} | Population: {population}\n"
            f"    Quality: {quality} | Impact: {impact}\n"
            f"    Summary: {extended_summary}"
        )

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


async def final_report(state: AgentState, config: RunnableConfig) -> dict:
    """Write the final report from all iteration evidence, drafts, critiques, and paper profiles."""
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config)

    compress_history = state.get("compress_findings_history", [])
    draft_history = state.get("draft_report_history", [])
    critique_history = state.get("critique_history", [])
    paper_profiles = state.get("paper_profiles", [])
    tqm = state.get("tiered_question_map") or {}

    # Build iteration history block
    history_parts = []
    for i, (cf, dr) in enumerate(zip(compress_history, draft_history)):
        history_parts.append(f"### Iteration {i + 1} — Evidence Summary\n{cf}")
        history_parts.append(f"### Iteration {i + 1} — Draft Report\n{dr}")
        if i < len(critique_history):
            history_parts.append(f"### Critique after Iteration {i + 1}\n{critique_history[i]}")

    iteration_history = "\n\n---\n\n".join(history_parts) if history_parts else "No iteration history available."

    # Build paper tier reference from extracted profiles (pre-numbered [1]-[N])
    paper_tier_reference, _source_index = _build_paper_tier_reference(paper_profiles)

    # Build tiered questions block
    tiered_questions = _build_tiered_questions(tqm)

    prompt = final_report_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        n_iterations=len(draft_history),
        iteration_history=iteration_history,
        paper_tier_reference=paper_tier_reference,
        tiered_questions=tiered_questions,
        max_sources=configurable.max_sources,
    )

    response = await model.ainvoke([HumanMessage(content=prompt)])
    content = str(response.content)

    return {
        "final_report": content,
        "messages": [AIMessage(content=content)],
    }

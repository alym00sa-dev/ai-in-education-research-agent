"""QA audit node — verifies the final report against source material."""

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from prompts.qa import qa_audit_prompt
from state import AgentState, QAScores
from utils.llm import get_judge_model
from nodes.report import _build_paper_tier_reference
from utils.citations import build_notes_index


_SCORE_PROMPT = """Based on your audit above, assign scores for each dimension.

Scoring guidance:
- Citation linkage (0-20): deduct 2 pts per orphan citation or missing bibliography entry
- Statistic provenance (0-25): (verified_count / total_count) × 25; if no statistics cited score 20
- Study design accuracy (0-15): deduct 5 pts per mislabelled RCT/QED
- Sub-question coverage (0-20): (fully_covered_tiers / total_tiers) × 20
- URL integrity (0-20): deduct 4 pts per MISMATCH or INVENTED URL

Return only the 5 integer scores."""


def _build_notes_tier_reference(notes_index: dict[int, dict]) -> str:
    """Format the notes_index as a compact reference block for the QA prompt."""
    if not notes_index:
        return "No supplementary sources."
    lines = []
    for n, p in sorted(notes_index.items()):
        title = (p.get("title") or "Unknown")[:100]
        authors = (p.get("authors") or "")[:60]
        year = p.get("year") or "n.d."
        url = p.get("url") or "not available"
        lines.append(f"[{n}] {title} ({year}). {authors}\n    URL: {url}")
    return "\n\n".join(lines)


async def qa_audit(state: AgentState, config: RunnableConfig) -> dict:
    """Audit the final report for citation accuracy, stat provenance, and coverage.

    Uses Claude claude-opus-4-6 as an independent judge to avoid self-evaluation bias.
    Two-step: (1) free-text prose audit, (2) structured scores-only extraction.
    """
    judge = get_judge_model()
    scoring_model = judge.with_structured_output(QAScores)

    final_report = state.get("final_report", "")
    paper_profiles = state.get("paper_profiles", [])
    all_notes = state.get("all_notes", [])
    exec_history = state.get("executive_summary_history", [])
    critique_history = state.get("critique_history", [])

    # Rebuild the same reference blocks used during report generation
    paper_tier_reference, index_map = _build_paper_tier_reference(paper_profiles)
    max_profile_n = max(index_map.keys()) if index_map else 0

    notes_index = build_notes_index(all_notes, exec_history, index_map)
    notes_start = (max_profile_n + 1) if notes_index else (max_profile_n + 1)
    notes_tier_reference = _build_notes_tier_reference(notes_index)

    # Build iteration history from executive summaries + critiques
    history_parts = []
    for i, es in enumerate(exec_history):
        history_parts.append(f"### Iteration {i + 1} — Executive Summary\n{es}")
        if i < len(critique_history):
            history_parts.append(f"### Critique after Iteration {i + 1}\n{critique_history[i]}")
    iteration_history = "\n\n---\n\n".join(history_parts) if history_parts else "No iteration history available."

    prompt = qa_audit_prompt.format(
        final_report=final_report,
        paper_tier_reference=paper_tier_reference,
        notes_tier_reference=notes_tier_reference[:20000],
        iteration_history=iteration_history[:35000],
        max_profile_n=max_profile_n,
        notes_start=notes_start,
    )

    # Step 1 — prose audit (free text)
    audit_response = await judge.ainvoke([HumanMessage(content=prompt)])
    audit_markdown = str(audit_response.content)

    # Step 2 — extract scores only (small structured output, reliable with Claude)
    scores: QAScores = await scoring_model.ainvoke([
        HumanMessage(content=prompt),
        audit_response,
        HumanMessage(content=_SCORE_PROMPT),
    ])
    overall = scores.overall_score

    score_summary = (
        f"\n\n---\n\n## Score Summary\n\n"
        f"| Dimension | Score |\n"
        f"|-----------|-------|\n"
        f"| Citation–bibliography linkage | {scores.citation_score}/20 |\n"
        f"| Statistic provenance | {scores.statistic_score}/25 |\n"
        f"| Study design accuracy | {scores.study_design_score}/15 |\n"
        f"| Sub-question coverage | {scores.coverage_score}/20 |\n"
        f"| URL integrity | {scores.url_score}/20 |\n"
        f"| **Overall** | **{overall}/100** |\n"
    )

    return {
        "qa_report": audit_markdown + score_summary,
        "qa_score": overall,
    }

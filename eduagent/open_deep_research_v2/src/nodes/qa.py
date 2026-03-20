"""QA audit node — verifies the final report against source material."""

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from prompts.qa import qa_audit_prompt
from state import AgentState
from utils.llm import get_model
from nodes.report import _build_paper_tier_reference, _strip_inline_citations


async def qa_audit(state: AgentState, config: RunnableConfig) -> dict:
    """Audit the final report for citation accuracy, stat provenance, and coverage."""
    model = get_model(config)

    final_report = state.get("final_report", "")
    paper_profiles = state.get("paper_profiles", [])
    compress_history = state.get("compress_findings_history", [])
    draft_history = state.get("draft_report_history", [])
    critique_history = state.get("critique_history", [])

    # Rebuild the same reference block used during report generation
    paper_tier_reference, _ = _build_paper_tier_reference(paper_profiles)

    # Reconstruct iteration history
    history_parts = []
    for i, (cf, dr) in enumerate(zip(compress_history, draft_history)):
        history_parts.append(f"### Iteration {i + 1} — Evidence Summary\n{_strip_inline_citations(cf)}")
        history_parts.append(f"### Iteration {i + 1} — Draft Report\n{_strip_inline_citations(dr)}")
        if i < len(critique_history):
            history_parts.append(f"### Critique after Iteration {i + 1}\n{_strip_inline_citations(critique_history[i])}")
    iteration_history = "\n\n---\n\n".join(history_parts) if history_parts else "No iteration history available."

    prompt = qa_audit_prompt.format(
        final_report=final_report,
        paper_tier_reference=paper_tier_reference,
        iteration_history=iteration_history[:40000],  # cap to avoid context overflow
    )

    response = await model.ainvoke([HumanMessage(content=prompt)])
    audit_report = str(response.content)

    return {"qa_report": audit_report}

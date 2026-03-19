"""Critique node — evaluates evidence summary + draft report and directs next iteration."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import critique_prompt, lead_researcher_prompt
from state import AgentState, CritiqueOutput
from utils.llm import get_model, get_today_str


async def critique(state: AgentState, config: RunnableConfig) -> dict:
    """Evaluate the current iteration's evidence summary and draft report.

    Produces:
    - critique_history entry: identified gaps, errors, missing angles
    - Updated supervisor_messages for next iteration (targeted brief)
    - Incremented iteration counter
    - Cleared notes (ready for next iteration's researchers)
    """
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config).with_structured_output(CritiqueOutput)

    iteration = state.get("iteration", 0)
    compress_history = state.get("compress_findings_history", [])
    draft_history = state.get("draft_report_history", [])
    tqm = state.get("tiered_question_map", {})

    current_compress = compress_history[-1] if compress_history else ""
    current_draft = draft_history[-1] if draft_history else ""

    prompt = critique_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        iteration=iteration + 1,
        total_iterations=configurable.research_iterations,
        compress_findings=current_compress,
        draft_report=current_draft,
    )

    result: CritiqueOutput = await model.ainvoke([HumanMessage(content=prompt)])

    critique_text = (
        f"## Critique — Iteration {iteration + 1}\n\n"
        f"**Evidence Gaps:**\n" +
        "\n".join(f"- {g}" for g in result.evidence_gaps) +
        f"\n\n**Reasoning Errors:**\n" +
        "\n".join(f"- {e}" for e in result.reasoning_errors) +
        f"\n\n**Missing Angles:**\n" +
        "\n".join(f"- {a}" for a in result.missing_angles) +
        f"\n\n**Next Iteration Brief:**\n{result.next_iteration_brief}"
    )

    def fmt(questions: list[str]) -> str:
        return "\n".join(f"  - {q}" for q in questions) if questions else "  (covered in prior iteration)"

    supervisor_system = lead_researcher_prompt.format(
        research_brief=state.get("research_brief", ""),
        tier1_questions=fmt(tqm.get("tier1", [])),
        tier2_questions=fmt(tqm.get("tier2", [])),
        tier3_questions=fmt(tqm.get("tier3", [])),
        tier4_questions=fmt(tqm.get("tier4", [])),
        max_concurrent_researchers=configurable.max_concurrent_researchers,
        iteration_context=(
            f"\n## Context from Iteration {iteration + 1}\n"
            f"A draft report was produced. DO NOT re-investigate questions already covered adequately.\n\n"
            f"**Critique identified these gaps to address:**\n{critique_text}\n\n"
            f"**Your focus for this iteration:** {result.next_iteration_brief}\n"
        ),
        date=get_today_str(),
    )

    return {
        "critique_history": [critique_text],
        "iteration": iteration + 1,
        # Clear notes so next iteration starts fresh
        "notes": {"type": "override", "value": []},
        "supervisor_messages": {
            "type": "override",
            "value": [
                SystemMessage(content=supervisor_system),
                HumanMessage(content=result.next_iteration_brief),
            ],
        },
    }

"""Critique node — evaluates current evidence and directs next iteration."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import critique_prompt, lead_researcher_prompt
from state import AgentState, CritiqueOutput
from utils.llm import get_model, get_today_str
from nodes.report import _build_paper_tier_reference, _build_tiered_questions


async def critique(state: AgentState, config: RunnableConfig) -> dict:
    """Evaluate the current evidence base and produce a directed brief for the next iteration.

    Reads directly from paper_profiles (structured) + all_notes (supplemental) +
    the latest executive summary — no lossy compress/draft intermediate.
    """
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config).with_structured_output(CritiqueOutput)

    iteration = state.get("iteration", 0)
    paper_profiles = state.get("paper_profiles", [])
    all_notes = state.get("all_notes", [])
    exec_history = state.get("executive_summary_history", [])
    tqm = state.get("tiered_question_map", {})

    paper_tier_reference, _ = _build_paper_tier_reference(paper_profiles)
    tiered_questions = _build_tiered_questions(tqm)

    current_exec = exec_history[-1] if exec_history else "No executive summary yet."
    notes_text = "\n\n---\n\n".join(all_notes[-10:]) if all_notes else "No supplemental notes yet."

    prompt = critique_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        iteration=iteration + 1,
        total_iterations=configurable.research_iterations,
        paper_tier_reference=paper_tier_reference,
        research_notes=notes_text,
        executive_summary=current_exec,
        tiered_questions=tiered_questions,
    )

    result: CritiqueOutput = await model.ainvoke([HumanMessage(content=prompt)])

    critique_text = (
        f"## Critique — Iteration {iteration + 1}\n\n"
        f"**Evidence Gaps:**\n" +
        "\n".join(f"- {g}" for g in result.evidence_gaps) +
        f"\n\n**Thesis Gaps:**\n" +
        "\n".join(f"- {g}" for g in result.thesis_gaps) +
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
            f"Research has been conducted and an executive summary produced. "
            f"DO NOT re-investigate questions already adequately covered.\n\n"
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

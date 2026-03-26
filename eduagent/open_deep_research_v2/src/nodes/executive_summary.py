"""Executive summary node — lightweight synthesis of current evidence state."""

import logging
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts.executive_summary import executive_summary_prompt
from state import AgentState
from utils.llm import get_model, get_today_str
from utils.ranking import rank_profiles
from nodes.report import _build_paper_tier_reference, _build_tiered_questions

logger = logging.getLogger(__name__)


async def executive_summary(state: AgentState, config: RunnableConfig) -> dict:
    """Synthesise current paper profiles + notes into a concise executive summary.

    The LLM writes using (Author, Year) citations throughout — no [N] injection here.
    [N] numbers are only assigned once, in the final report post-processing step,
    against the stable full_index_map. Injecting [N] here causes stale numbers to
    propagate forward as more paper_profiles are added across iterations.
    """
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config)

    paper_profiles = state.get("paper_profiles", [])
    all_notes = state.get("all_notes", [])
    iteration = state.get("iteration", 0)
    tqm = state.get("tiered_question_map") or {}

    ranked_profiles = rank_profiles(paper_profiles, state.get("research_brief", ""), tqm)
    paper_tier_reference, _ = _build_paper_tier_reference(ranked_profiles)
    tiered_questions = _build_tiered_questions(tqm)

    notes_text = "\n\n---\n\n".join(all_notes[-10:]) if all_notes else "No supplemental notes yet."

    prompt = executive_summary_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        iteration=iteration + 1,
        total_iterations=configurable.research_iterations,
        paper_tier_reference=paper_tier_reference,
        research_notes=notes_text,
        tiered_questions=tiered_questions,
    )

    response = await model.ainvoke([HumanMessage(content=prompt)])
    raw_summary = str(response.content)

    logger.info(f"[exec_summary] iter={iteration+1} — summary generated in (Author, Year) format")

    return {"executive_summary_history": [raw_summary]}

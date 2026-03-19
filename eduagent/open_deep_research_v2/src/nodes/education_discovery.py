"""Education discovery node — transforms user query into research brief + tiered question map."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from configuration import Configuration
from prompts import lead_researcher_prompt, research_brief_prompt
from state import AgentState, ResearchBrief
from utils.llm import get_model, get_today_str


async def education_discovery(
    state: AgentState,
    config: RunnableConfig,
) -> Command[Literal["research_supervisor"]]:
    """Transform user messages into a structured research brief and tiered question map.

    Produces:
    - research_brief: structured research question with population/context/scope
    - tiered_question_map: tier1-4 questions for the supervisor to dispatch
    - supervisor_messages: initialized with lead_researcher_prompt as system context
    """
    configurable = Configuration.from_runnable_config(config)

    model = (
        get_model(config)
        .with_structured_output(ResearchBrief)
        .with_retry(stop_after_attempt=3)
    )

    prompt = research_brief_prompt.format(
        messages=get_buffer_string(state.get("messages", [])),
        date=get_today_str(),
    )
    result: ResearchBrief = await model.ainvoke([HumanMessage(content=prompt)])

    def fmt(questions: list[str]) -> str:
        return "\n".join(f"  - {q}" for q in questions) if questions else "  (none)"

    supervisor_system = lead_researcher_prompt.format(
        research_brief=result.key_research_priority,
        tier1_questions=fmt(result.tier1),
        tier2_questions=fmt(result.tier2),
        tier3_questions=fmt(result.tier3),
        tier4_questions=fmt(result.tier4),
        max_concurrent_researchers=configurable.max_concurrent_researchers,
        iteration_context="",
        date=get_today_str(),
    )

    full_brief = "\n".join([
        f"Topic: {result.topic}",
        f"Focal Intervention: {result.focal_intervention}",
        f"Population: {result.population}",
        f"Context: {result.context}",
        f"Target Skills / Outcomes: {result.target_skills_outcomes}",
        f"Likely Comparators: {result.likely_comparators}",
        f"Key Research Priority: {result.key_research_priority}",
    ])

    return Command(
        goto="research_supervisor",
        update={
            "research_brief": full_brief,
            "tiered_question_map": result.model_dump(),
            "iteration": 0,
            "supervisor_messages": {
                "type": "override",
                "value": [
                    SystemMessage(content=supervisor_system),
                    HumanMessage(content=full_brief),
                ],
            },
        },
    )

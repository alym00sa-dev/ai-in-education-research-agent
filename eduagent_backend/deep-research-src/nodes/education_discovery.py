"""Education discovery node — transforms user query into research brief + tiered question map."""

import uuid
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from configuration import Configuration
from prompts import lead_researcher_prompt, research_brief_prompt
from state import AgentState, ResearchBrief
from utils.llm import get_model, get_today_str
from utils.kg_retriever import query_kg_for_topic, format_kg_evidence_block
from utils.budget import reset_budget
from utils import run_logger


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

    # Initialize per-session run log (frontend runs only — no-op if no session_id)
    if configurable.session_id:
        run_logger.init(configurable.session_id)

    messages = state.get("messages", [])
    query_text = messages[0].content if messages else ""
    run_logger.log(f"Query: {query_text}", configurable.session_id)

    # Reset tool budgets at the start of every run (works for both server and run_pipeline.py)
    reset_budget(
        tavily_limit=configurable.tavily_budget,
        serp_limit=configurable.serp_budget,
    )

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

    # ── A7: KG-first lookup ────────────────────────────────────────────────────
    # Query Neo4j for corpus papers already relevant to this brief.
    # Papers are added to paper_profiles so they compete freely for the top-k
    # source pool in the final report (full circle: KG → retrieved → cited).
    # Fails silently if Neo4j is unavailable.
    topic_keywords = [result.topic, result.target_skills_outcomes, result.context]
    kg_papers = query_kg_for_topic(
        focal_intervention=result.focal_intervention,
        population=result.population,
        topic_keywords=topic_keywords,
        session_id=configurable.session_id,
    )
    kg_evidence_block = format_kg_evidence_block(kg_papers)

    # Append KG evidence to supervisor system prompt so researchers know what's
    # already covered and can focus on gaps
    if kg_evidence_block:
        supervisor_system = supervisor_system + "\n\n" + kg_evidence_block

    run_logger.log("[education_discovery] Research query breakdown completed.", configurable.session_id)
    for line in full_brief.splitlines():
        run_logger.log(f"           {line}", configurable.session_id)

    return Command(
        goto="research_supervisor",
        update={
            "session_id": state.get("session_id") or str(uuid.uuid4()),
            "research_brief": full_brief,
            "tiered_question_map": result.model_dump(),
            "iteration": 0,
            "paper_profiles": kg_papers,  # seed source pool with KG papers
            "supervisor_messages": {
                "type": "override",
                "value": [
                    SystemMessage(content=supervisor_system),
                    HumanMessage(content=full_brief),
                ],
            },
        },
    )

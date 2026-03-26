"""Deep Researcher — graph definition and compilation.

To add a new research phase, create a file in nodes/ and wire it in here.

Current workflow:
    education_discovery → research_supervisor → supervisor_critique → final_report_generation
"""

import os
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

from configuration import Configuration
from langchain_core.runnables import RunnableConfig
from state import AgentInputState, AgentState
from nodes.education_discovery import education_discovery
from nodes.supervisor import supervisor_subgraph
from nodes.report import final_report_generation
# swanson_abc and qa_review preserved for future use — not wired into graph
from prompts import critique_agent_prompt, critique_agent_search_prompt, lead_researcher_prompt


class CritiqueDecision(BaseModel):
    depth_assessment: str = Field(default="", description="1-2 sentence summary of what the current findings cover well and where depth is lacking")
    depth_directives: list[str] = Field(default_factory=list, description="3-5 specific new angles, questions, or constructs to explore next")
    recommended_keywords: list[str] = Field(default_factory=list, description="5-10 specific search keywords or phrases the next round should try")
    search_directive: str = Field(default="", description="2-3 specific database query strings for the next research round")


async def supervisor_critique(
    state: AgentState,
    config: RunnableConfig,
) -> Command[Literal["research_supervisor", "final_report_generation"]]:
    """Depth director at the synthesis level.

    Runs after each research round (except the last). Does NOT decide pass/fail.
    Always produces a depth directive — new angles, keywords, and query strings —
    and sends the supervisor back for another targeted research round.
    The only exit is hitting the max_critique_cycles budget.
    """
    configurable = Configuration.from_runnable_config(config)
    critique_cycles = state.get("critique_cycles", 0)
    max_critique_cycles = configurable.research_iterations - 1

    if critique_cycles >= max_critique_cycles:
        return Command(goto="final_report_generation", update={})

    notes = state.get("notes", [])
    research_brief = state.get("research_brief", "")

    findings_summary = "\n\n".join(str(n) for n in notes)
    if len(findings_summary) > 20000:
        findings_summary = findings_summary[:20000] + "\n[truncated]"

    if not findings_summary.strip():
        return Command(goto="final_report_generation", update={})

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    import logging as _log

    # ── Phase 1: web search for adjacent/complementary evidence (optional) ────
    counter_evidence = ""
    try:
        search_prompt = critique_agent_search_prompt.format(
            research_topic=research_brief,
            findings_summary=findings_summary,
        )
        search_model = init_chat_model(
            model="anthropic:claude-sonnet-4-6",
            max_tokens=2048,
            api_key=anthropic_api_key,
            tags=["langsmith:nostream"],
        ).bind_tools([{"type": "web_search_20250305", "name": "web_search"}])

        search_response = await search_model.ainvoke([HumanMessage(content=search_prompt)])

        if isinstance(search_response.content, str):
            counter_evidence = search_response.content
        elif isinstance(search_response.content, list):
            counter_evidence = " ".join(
                block.get("text", "") for block in search_response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
    except Exception as _e:
        _log.warning(f"[supervisor_critique] web search failed (continuing without): {type(_e).__name__}: {_e}")

    # ── Phase 2: depth directive decision ─────────────────────────────────────
    try:
        counter_evidence_block = (
            f"<AdjacentEvidence>\n{counter_evidence.strip()}\n</AdjacentEvidence>"
            if counter_evidence.strip()
            else ""
        )
        decision_prompt = critique_agent_prompt.format(
            research_topic=research_brief,
            findings_summary=findings_summary,
            counter_evidence_block=counter_evidence_block,
        )
        decision_model = init_chat_model(
            model="anthropic:claude-sonnet-4-6",
            max_tokens=2048,
            api_key=anthropic_api_key,
            tags=["langsmith:nostream"],
        ).with_structured_output(CritiqueDecision)

        decision: CritiqueDecision = await decision_model.ainvoke([
            HumanMessage(content=decision_prompt)
        ])
    except Exception as _e:
        _log.error(f"[supervisor_critique] depth decision failed (cycle {critique_cycles}): {type(_e).__name__}: {_e}")
        return Command(goto="final_report_generation", update={"critique_cycles": critique_cycles + 1})

    # Always deepen — critique is a depth driver, not a gatekeeper.
    # Every cycle produces new angles/keywords to explore; the only exit is the iteration budget.
    directives_text = "\n".join(f"- {d}" for d in decision.depth_directives) or "None specified"
    keywords_text = ", ".join(decision.recommended_keywords) or "None specified"

    source_counts = state.get("source_counts", {})
    tavily_used = source_counts.get("tavily", 0)
    serpapi_used = source_counts.get("scholar_search", 0)
    tavily_remaining = max(0, configurable.tavily_budget - tavily_used)
    serpapi_remaining = max(0, configurable.serpapi_budget - serpapi_used)

    notes_count = len(notes)
    prior_coverage_summary = (
        f"The previous round produced {notes_count} research notes covering the initial sub-questions. "
        f"That work is complete and stored — do not re-run it."
    )

    depth_directive_content = (
        f"DEPTH DIRECTIVE (cycle {critique_cycles + 1}/{max_critique_cycles})\n\n"
        f"⚠️ CRITICAL: Do NOT re-decompose the research brief. Do NOT re-dispatch researchers "
        f"on sub-questions similar to those already investigated. {prior_coverage_summary}\n\n"
        f"Research brief: {research_brief}\n\n"
        f"**Assessment of current coverage:**\n{decision.depth_assessment}\n\n"
        f"**NEW angles to dispatch researchers on (ONLY these — no others):**\n{directives_text}\n\n"
        f"**Keywords/terms to try in next searches:**\n{keywords_text}\n\n"
        f"**Suggested query strings:**\n{decision.search_directive}\n\n"
        f"Dispatch researchers ONLY on the new angles listed above. Stay on the original research topic — "
        f"these are depth layers, not new topics.\n\n"
        f"**Remaining credits:** Tavily: {tavily_remaining}/{configurable.tavily_budget} · "
        f"SerpAPI: {serpapi_remaining}/{configurable.serpapi_budget}"
    )

    # Build the supervisor_system_prompt the same way education_discovery does,
    # then override supervisor_messages with a clean slate (system prompt + depth directive).
    # This avoids the orphaned-tool-call problem: the previous round's ResearchComplete
    # AIMessage has no ToolMessage response, which would corrupt the message history
    # if we just appended to it.
    credit_budget = (
        f"**Shared Credit Budget (remaining):**\n"
        f"- Tavily: {tavily_remaining} calls remaining\n"
        f"- SerpAPI (Google Scholar): {serpapi_remaining} calls remaining\n"
        f"- LLM web search (anthropic_web_search, openai_web_search): unlimited\n\n"
        f"**Allocation rules:**\n"
        f"- Tavily is now available — use it for targeted evidence gap searches\n"
        f"- LLM web search is always available to all researchers at no credit cost"
    )
    supervisor_system_prompt = lead_researcher_prompt.format(
        date=__import__("datetime").date.today().strftime("%B %d, %Y"),
        max_concurrent_research_units=configurable.max_concurrent_research_units,
        max_researcher_iterations=configurable.max_researcher_iterations,
        credit_budget=credit_budget,
    )

    return Command(
        goto="research_supervisor",
        update={
            "critique_cycles": critique_cycles + 1,
            "supervisor_messages": {
                "type": "override",
                "value": [
                    SystemMessage(content=supervisor_system_prompt),
                    HumanMessage(content=depth_directive_content),
                ],
            },
        },
    )


deep_researcher_builder = StateGraph(
    AgentState,
    input=AgentInputState,
    config_schema=Configuration
)

deep_researcher_builder.add_node("education_discovery", education_discovery)
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("supervisor_critique", supervisor_critique)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

deep_researcher_builder.add_edge(START, "education_discovery")
deep_researcher_builder.add_edge("research_supervisor", "supervisor_critique")
deep_researcher_builder.add_edge("final_report_generation", END)

deep_researcher = deep_researcher_builder.compile()

"""Research supervisor subgraph — decomposes research brief into threads and dispatches researchers."""

import asyncio
import logging
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool as lc_tool
from langgraph.graph import END, START, StateGraph

from configuration import Configuration
from state import ConductResearch, ResearchComplete, SupervisorState
from utils.llm import get_model, is_token_limit_exceeded, think_tool

logger = logging.getLogger(__name__)

_MAX_SUPERVISOR_LOOPS = 6


async def supervisor_node(
    state: SupervisorState,
    config: RunnableConfig,
) -> dict:
    """LLM supervisor — decides which research threads to dispatch."""
    model = get_model(config)
    bound_model = model.bind_tools([
        lc_tool(ConductResearch),
        lc_tool(ResearchComplete),
        think_tool,
    ])

    messages = state.get("supervisor_messages", [])
    response = await bound_model.ainvoke(messages)
    return {"supervisor_messages": [response]}


async def supervisor_tools_node(
    state: SupervisorState,
    config: RunnableConfig,
) -> dict:
    """Execute supervisor tool calls — dispatch researchers and collect results."""
    from nodes.researcher import researcher_subgraph

    configurable = Configuration.from_runnable_config(config)
    messages = state.get("supervisor_messages", [])

    # Find the most recent AI message and check if it has tool calls
    last_ai = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            # Only process tool calls from the MOST RECENT AIMessage.
            # If it has no tool_calls, bail — do not look further back,
            # as adding ToolMessages after a plain AIMessage would create
            # an orphaned-tool-role error in the OpenAI API.
            if msg.tool_calls:
                last_ai = msg
            break

    if not last_ai:
        return {}

    tool_calls = last_ai.tool_calls
    tool_messages: list[ToolMessage] = []
    aggregated_notes: list[str] = []
    aggregated_raw_notes: list[str] = []
    aggregated_source_counts: dict = {}
    aggregated_paper_profiles: list = []
    aggregated_thought_log: list = []
    aggregated_filter_log: list = []

    # Separate tool types
    think_calls = [tc for tc in tool_calls if tc["name"] == "think_tool"]
    conduct_calls = [tc for tc in tool_calls if tc["name"] == "ConductResearch"]
    complete_calls = [tc for tc in tool_calls if tc["name"] == "ResearchComplete"]

    # Handle think_tool calls
    for tc in think_calls:
        reflection = tc["args"].get("reflection", "")
        tool_messages.append(ToolMessage(
            content=f"Reflection recorded: {reflection}",
            name="think_tool",
            tool_call_id=tc["id"],
        ))

    # Handle ResearchComplete
    if complete_calls:
        for tc in complete_calls:
            tool_messages.append(ToolMessage(
                content="Research marked complete.",
                name="ResearchComplete",
                tool_call_id=tc["id"],
            ))

    # Handle ConductResearch — enforce max_concurrent_researchers
    # If supervisor dispatches too many, reject ALL and send feedback so it re-dispatches correctly
    max_researchers = configurable.max_concurrent_researchers
    if len(conduct_calls) > max_researchers:
        for tc in conduct_calls:
            tool_messages.append(ToolMessage(
                content=(
                    f"Too many research threads dispatched ({len(conduct_calls)}). "
                    f"Maximum allowed is {max_researchers}. "
                    f"Please re-dispatch with at most {max_researchers} threads."
                ),
                name="ConductResearch",
                tool_call_id=tc["id"],
            ))
        return {"supervisor_messages": tool_messages}

    active_calls = conduct_calls

    if active_calls:
        async def invoke_researcher(tc: dict):
            args = tc["args"]
            research_topic = args.get("research_topic", "")
            tier = args.get("tier", "tier3")
            keywords = args.get("keywords", [])

            initial_brief = research_topic
            if keywords:
                initial_brief += f"\n\nSuggested keywords: {', '.join(keywords)}"

            initial_state = {
                "researcher_messages": [HumanMessage(content=initial_brief)],
                "research_topic": research_topic,
                "tier": tier,
                "sweep_cycles": 0,
                "web_search_calls": 0,
                "source_counts": {},
                "thought_log": [],
                "filtered_papers_log": [],
                "paper_profiles": [],
                "keyword_history": [],
                "current_keyword_set": None,
                "compressed_research": "",
                "raw_notes": [],
            }
            try:
                return tc, await researcher_subgraph.ainvoke(initial_state, config)
            except Exception as e:
                logger.error(f"[supervisor_tools] Researcher failed for '{research_topic}': {e}")
                return tc, {"compressed_research": f"Researcher error: {e}", "raw_notes": [],
                            "source_counts": {}, "paper_profiles": [], "thought_log": [],
                            "filtered_papers_log": []}

        results = await asyncio.gather(*[invoke_researcher(tc) for tc in active_calls])

        for tc, result in results:
            compressed = result.get("compressed_research", "")
            tool_messages.append(ToolMessage(
                content=compressed or "No findings returned.",
                name="ConductResearch",
                tool_call_id=tc["id"],
            ))

            if compressed:
                aggregated_notes.append(compressed)

            raw = result.get("raw_notes", [])
            if isinstance(raw, list):
                aggregated_raw_notes.extend(raw)

            for k, v in (result.get("source_counts") or {}).items():
                aggregated_source_counts[k] = aggregated_source_counts.get(k, 0) + v

            aggregated_paper_profiles.extend(result.get("paper_profiles") or [])
            aggregated_thought_log.extend(result.get("thought_log") or [])
            aggregated_filter_log.extend(result.get("filtered_papers_log") or [])

    updates: dict = {"supervisor_messages": tool_messages}
    if aggregated_notes:
        updates["notes"] = aggregated_notes
    if aggregated_raw_notes:
        updates["raw_notes"] = aggregated_raw_notes
    if aggregated_source_counts:
        updates["source_counts"] = aggregated_source_counts
    if aggregated_paper_profiles:
        updates["paper_profiles"] = aggregated_paper_profiles
    if aggregated_thought_log:
        updates["thought_log"] = aggregated_thought_log
    if aggregated_filter_log:
        updates["filtered_papers_log"] = aggregated_filter_log

    return updates


def route_supervisor(state: SupervisorState) -> Literal["supervisor_node", "__end__"]:
    """Continue supervisor loop or end the subgraph."""
    messages = state.get("supervisor_messages", [])
    iterations = state.get("research_iterations", 0)

    if iterations >= _MAX_SUPERVISOR_LOOPS:
        return "__end__"

    # Check last AI message
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if not msg.tool_calls:
                return "__end__"
            tool_names = {tc["name"] for tc in msg.tool_calls}
            if "ResearchComplete" in tool_names:
                return "__end__"
            # If only think_tool was called and no ConductResearch, keep going
            return "supervisor_node"

    return "__end__"


def route_after_tools(state: SupervisorState) -> Literal["supervisor_node", "__end__"]:
    """After tools execute, check if we should loop back to supervisor."""
    messages = state.get("supervisor_messages", [])
    iterations = state.get("research_iterations", 0)

    if iterations >= _MAX_SUPERVISOR_LOOPS:
        return "__end__"

    # Check if last AI message had ResearchComplete or no tool_calls (plain text)
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if not msg.tool_calls:
                return "__end__"
            tool_names = {tc["name"] for tc in msg.tool_calls}
            if "ResearchComplete" in tool_names:
                return "__end__"
            break

    return "supervisor_node"


def increment_iterations(state: SupervisorState) -> dict:
    """Increment supervisor loop counter (called on entry to supervisor_node)."""
    return {"research_iterations": state.get("research_iterations", 0) + 1}


# Build the supervisor subgraph
_supervisor_builder = StateGraph(SupervisorState, config_schema=Configuration)

_supervisor_builder.add_node("supervisor_node", supervisor_node)
_supervisor_builder.add_node("supervisor_tools", supervisor_tools_node)

_supervisor_builder.add_edge(START, "supervisor_node")
_supervisor_builder.add_edge("supervisor_node", "supervisor_tools")
_supervisor_builder.add_conditional_edges(
    "supervisor_tools",
    route_after_tools,
    {"supervisor_node": "supervisor_node", "__end__": END},
)

supervisor_subgraph = _supervisor_builder.compile()

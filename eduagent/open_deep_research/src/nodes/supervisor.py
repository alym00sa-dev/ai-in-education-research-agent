"""Supervisor nodes — lead researcher subgraph that delegates to individual researchers."""

import asyncio
from typing import Literal

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from configuration import Configuration
from state import ConductResearch, ResearchComplete, SupervisorState
from utils.llm import (
    configurable_model,
    get_api_key_for_model,
    get_notes_from_tool_calls,
    is_token_limit_exceeded,
    think_tool,
)
from nodes.researcher import researcher_subgraph


async def supervisor(
    state: SupervisorState,
    config: RunnableConfig,
) -> Command[Literal["supervisor_tools"]]:
    """Lead research supervisor that plans research strategy and delegates to researchers.

    Analyzes the research brief and decides how to break down the research into
    manageable tasks. Can use think_tool for strategic planning, ConductResearch
    to delegate tasks, or ResearchComplete when satisfied with findings.

    Args:
        state: Current supervisor state with messages and research context
        config: Runtime configuration with model settings

    Returns:
        Command to proceed to supervisor_tools for tool execution
    """
    configurable = Configuration.from_runnable_config(config)
    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    lead_researcher_tools = [ConductResearch, ResearchComplete, think_tool]

    research_model = (
        configurable_model
        .bind_tools(lead_researcher_tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )

    supervisor_messages = state.get("supervisor_messages", [])
    response = await research_model.ainvoke(supervisor_messages)

    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )


async def supervisor_tools(
    state: SupervisorState,
    config: RunnableConfig,
) -> Command[Literal["supervisor", "__end__"]]:
    """Execute tools called by the supervisor.

    Handles three types of tool calls:
    1. think_tool — strategic reflection, continues the conversation
    2. ConductResearch — delegates tasks to sub-researchers (run in parallel)
    3. ResearchComplete — signals completion of the research phase

    Args:
        state: Current supervisor state with messages and iteration count
        config: Runtime configuration with research limits and model settings

    Returns:
        Command to either continue supervision loop or end research phase
    """
    configurable = Configuration.from_runnable_config(config)
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]

    exceeded_allowed_iterations = research_iterations > configurable.max_researcher_iterations
    no_tool_calls = not most_recent_message.tool_calls
    research_complete_tool_call = any(
        tool_call["name"] == "ResearchComplete"
        for tool_call in most_recent_message.tool_calls
    )

    if exceeded_allowed_iterations or no_tool_calls or research_complete_tool_call:
        return Command(
            goto=END,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )

    all_tool_messages = []
    update_payload = {"supervisor_messages": []}

    # Handle think_tool calls
    think_tool_calls = [
        tool_call for tool_call in most_recent_message.tool_calls
        if tool_call["name"] == "think_tool"
    ]

    for tool_call in think_tool_calls:
        reflection_content = tool_call["args"]["reflection"]
        all_tool_messages.append(ToolMessage(
            content=f"Reflection recorded: {reflection_content}",
            name="think_tool",
            tool_call_id=tool_call["id"]
        ))

    # Handle ConductResearch calls (run in parallel)
    conduct_research_calls = [
        tool_call for tool_call in most_recent_message.tool_calls
        if tool_call["name"] == "ConductResearch"
    ]

    if conduct_research_calls:
        try:
            allowed_calls = conduct_research_calls[:configurable.max_concurrent_research_units]
            overflow_calls = conduct_research_calls[configurable.max_concurrent_research_units:]

            research_tasks = [
                researcher_subgraph.ainvoke({
                    "researcher_messages": [
                        HumanMessage(content=tool_call["args"]["research_topic"])
                    ],
                    "research_topic": tool_call["args"]["research_topic"]
                }, config)
                for tool_call in allowed_calls
            ]

            tool_results = await asyncio.gather(*research_tasks)

            for observation, tool_call in zip(tool_results, allowed_calls):
                all_tool_messages.append(ToolMessage(
                    content=observation.get(
                        "compressed_research",
                        "Error synthesizing research report: Maximum retries exceeded"
                    ),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                ))

            for overflow_call in overflow_calls:
                all_tool_messages.append(ToolMessage(
                    content=(
                        f"Error: Did not run this research as you have already exceeded the "
                        f"maximum number of concurrent research units. Please try again with "
                        f"{configurable.max_concurrent_research_units} or fewer research units."
                    ),
                    name="ConductResearch",
                    tool_call_id=overflow_call["id"]
                ))

            raw_notes_concat = "\n".join([
                "\n".join(observation.get("raw_notes", []))
                for observation in tool_results
            ])

            if raw_notes_concat:
                update_payload["raw_notes"] = [raw_notes_concat]

        except Exception as e:
            if is_token_limit_exceeded(e, configurable.research_model) or True:
                return Command(
                    goto=END,
                    update={
                        "notes": get_notes_from_tool_calls(supervisor_messages),
                        "research_brief": state.get("research_brief", "")
                    }
                )

    update_payload["supervisor_messages"] = all_tool_messages
    return Command(goto="supervisor", update=update_payload)


# Supervisor Subgraph
supervisor_builder = StateGraph(SupervisorState, config_schema=Configuration)

supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)

supervisor_builder.add_edge(START, "supervisor")

supervisor_subgraph = supervisor_builder.compile()

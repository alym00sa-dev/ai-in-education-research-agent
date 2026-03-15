"""Researcher nodes — individual researcher subgraph for conducting focused research."""

import asyncio
import json
import os
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, filter_messages
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from configuration import Configuration
from prompts import (
    compress_research_simple_human_message,
    compress_research_system_prompt,
    critique_agent_prompt,
    research_system_prompt,
)
from state import ResearchComplete, ResearcherOutputState, ResearcherState
from utils.llm import (
    anthropic_websearch_called,
    configurable_model,
    get_api_key_for_model,
    get_today_str,
    is_token_limit_exceeded,
    openai_websearch_called,
    remove_up_to_last_ai_message,
)
from utils.search import get_all_tools


class CritiqueDecision(BaseModel):
    decision: Literal["PASS", "NEEDS_WORK"]
    evidence_rungs_found: list
    gap_summary: str
    search_directive: str


async def researcher(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher_tools"]]:
    """Individual researcher that conducts focused research on a specific topic.

    Given a specific research topic by the supervisor, uses available tools
    (search, think_tool, MCP tools) to gather comprehensive information.

    Args:
        state: Current researcher state with messages and topic context
        config: Runtime configuration with model settings and tool availability

    Returns:
        Command to proceed to researcher_tools for tool execution
    """
    configurable = Configuration.from_runnable_config(config)
    researcher_messages = state.get("researcher_messages", [])

    tools = await get_all_tools(config)
    if len(tools) == 0:
        raise ValueError(
            "No tools found to conduct research: Please configure either your "
            "search API or add MCP tools to your configuration."
        )

    research_topic = state.get("research_topic", "")
    researcher_tag = f"researcher_topic:{research_topic}" if research_topic else ""

    researcher_tags = ["langsmith:nostream"]
    if researcher_tag:
        researcher_tags.append(researcher_tag)

    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": researcher_tags,
    }

    researcher_prompt = research_system_prompt.format(
        mcp_prompt=configurable.mcp_prompt or "",
        date=get_today_str()
    )

    research_model = (
        configurable_model
        .bind_tools(tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )

    messages = [SystemMessage(content=researcher_prompt)] + researcher_messages
    response = await research_model.ainvoke(messages)

    return Command(
        goto="researcher_tools",
        update={
            "researcher_messages": [response],
            "tool_call_iterations": state.get("tool_call_iterations", 0) + 1
        }
    )


async def execute_tool_safely(tool, args, config):
    """Safely execute a tool with error handling."""
    try:
        return await tool.ainvoke(args, config)
    except Exception as e:
        return f"Error executing tool: {str(e)}"


async def researcher_tools(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher", "compress_research"]]:
    """Execute tools called by the researcher.

    Handles think_tool (strategic reflection), search tools, MCP tools,
    and ResearchComplete (signals end of research task).

    Args:
        state: Current researcher state with messages and iteration count
        config: Runtime configuration with research limits and tool settings

    Returns:
        Command to either continue research loop or proceed to compression
    """
    configurable = Configuration.from_runnable_config(config)
    researcher_messages = state.get("researcher_messages", [])
    most_recent_message = researcher_messages[-1]

    has_tool_calls = bool(most_recent_message.tool_calls)
    has_native_search = (
        openai_websearch_called(most_recent_message) or
        anthropic_websearch_called(most_recent_message)
    )

    if not has_tool_calls and not has_native_search:
        return Command(goto="compress_research")

    tools = await get_all_tools(config)
    tools_by_name = {
        tool.name if hasattr(tool, "name") else tool.get("name", "web_search"): tool
        for tool in tools
    }

    tool_calls = most_recent_message.tool_calls
    tool_execution_tasks = []
    for tool_call in tool_calls:
        args = dict(tool_call["args"])
        # Inject max_results for Tavily (InjectedToolArg default=5 is never set otherwise).
        # Scale per-query results off max_sources: floor(max_sources/3), capped at Tavily's max of 10.
        if tool_call["name"] == "tavily_search":
            args["max_results"] = max(5, min(10, configurable.max_sources // 3))
        tool_execution_tasks.append(
            execute_tool_safely(tools_by_name[tool_call["name"]], args, config)
        )
    observations = await asyncio.gather(*tool_execution_tasks)

    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        )
        for observation, tool_call in zip(observations, tool_calls)
    ]

    exceeded_iterations = state.get("tool_call_iterations", 0) >= configurable.max_react_tool_calls
    research_complete_called = any(
        tool_call["name"] == "ResearchComplete"
        for tool_call in most_recent_message.tool_calls
    )

    if exceeded_iterations or research_complete_called:
        return Command(
            goto="critique_agent",
            update={"researcher_messages": tool_outputs}
        )

    return Command(
        goto="researcher",
        update={"researcher_messages": tool_outputs}
    )


async def critique_agent(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher", "compress_research"]]:
    """Critique the sub-researcher's findings and decide whether to request a targeted follow-up.

    Uses Claude Haiku (always, regardless of main model choice) to evaluate evidence quality
    against the Evidence Ladder. Returns PASS → compress_research or NEEDS_WORK → researcher
    with a specific gap-fill instruction. Hard cap of 2 critique cycles.

    Args:
        state: Current researcher state with accumulated messages and critique cycle count
        config: Runtime configuration

    Returns:
        Command to compress_research (pass) or researcher (needs_work, cycles < 2)
    """
    critique_cycles = state.get("critique_cycles", 0)

    # Hard cap — never loop more than twice
    if critique_cycles >= 2:
        return Command(goto="compress_research", update={})

    researcher_messages = state.get("researcher_messages", [])
    research_topic = state.get("research_topic", "")

    # Build a findings summary from tool outputs (ToolMessages) — cap at 12k chars
    tool_outputs = [
        msg.content for msg in researcher_messages
        if hasattr(msg, "type") and msg.type == "tool"
    ]
    findings_summary = "\n\n".join(str(t) for t in tool_outputs)
    if len(findings_summary) > 12000:
        findings_summary = findings_summary[:12000] + "\n[truncated for brevity]"

    if not findings_summary.strip():
        return Command(goto="compress_research", update={})

    prompt = critique_agent_prompt.format(
        research_topic=research_topic,
        findings_summary=findings_summary,
    )

    try:
        critique_model = init_chat_model(
            model="anthropic:claude-haiku-4-5-20251001",
            max_tokens=512,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            tags=["langsmith:nostream"],
        ).with_structured_output(CritiqueDecision)

        decision: CritiqueDecision = await critique_model.ainvoke([
            HumanMessage(content=prompt)
        ])
    except Exception:
        # If critique fails for any reason, proceed to compression rather than block research
        return Command(goto="compress_research", update={})

    if decision.decision == "PASS":
        return Command(goto="compress_research", update={})

    # NEEDS_WORK — send a targeted gap-fill instruction back to the researcher
    gap_message = HumanMessage(content=(
        f"CRITIQUE FEEDBACK (cycle {critique_cycles + 1}/2): {decision.gap_summary}\n\n"
        f"Please run the following targeted search to fill this gap:\n{decision.search_directive}"
    ))
    return Command(
        goto="researcher",
        update={
            "researcher_messages": [gap_message],
            "critique_cycles": critique_cycles + 1,
            "tool_call_iterations": 0,  # Reset tool call counter for the follow-up round
        },
    )


async def compress_research(state: ResearcherState, config: RunnableConfig):
    """Compress and synthesize research findings into a concise, structured summary.

    Takes all research findings, tool outputs, and AI messages and distills them
    into a clean, comprehensive summary while preserving all important information.

    Args:
        state: Current researcher state with accumulated research messages
        config: Runtime configuration with compression model settings

    Returns:
        Dictionary containing compressed research summary and raw notes
    """
    configurable = Configuration.from_runnable_config(config)
    synthesizer_model = configurable_model.with_config({
        "model": configurable.compression_model,
        "max_tokens": configurable.compression_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.compression_model, config),
        "tags": ["langsmith:nostream"]
    })

    researcher_messages = state.get("researcher_messages", [])
    researcher_messages.append(HumanMessage(content=compress_research_simple_human_message))

    synthesis_attempts = 0
    max_attempts = 3

    while synthesis_attempts < max_attempts:
        try:
            compression_prompt = compress_research_system_prompt.format(date=get_today_str())
            messages = [SystemMessage(content=compression_prompt)] + researcher_messages

            response = await synthesizer_model.ainvoke(messages)

            raw_notes_content = "\n".join([
                str(message.content)
                for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
            ])

            return {
                "compressed_research": str(response.content),
                "raw_notes": [raw_notes_content]
            }

        except Exception as e:
            synthesis_attempts += 1

            if is_token_limit_exceeded(e, configurable.research_model):
                researcher_messages = remove_up_to_last_ai_message(researcher_messages)
                continue

            continue

    raw_notes_content = "\n".join([
        str(message.content)
        for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
    ])

    return {
        "compressed_research": "Error synthesizing research report: Maximum retries exceeded",
        "raw_notes": [raw_notes_content]
    }


# Researcher Subgraph
researcher_builder = StateGraph(
    ResearcherState,
    output=ResearcherOutputState,
    config_schema=Configuration
)

researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_tools", researcher_tools)
researcher_builder.add_node("critique_agent", critique_agent)
researcher_builder.add_node("compress_research", compress_research)

researcher_builder.add_edge(START, "researcher")
researcher_builder.add_edge("compress_research", END)

researcher_subgraph = researcher_builder.compile()

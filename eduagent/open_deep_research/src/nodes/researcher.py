"""Researcher nodes — individual researcher subgraph for conducting focused research."""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, filter_messages
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

from configuration import Configuration
from prompts import (
    compress_research_simple_human_message,
    compress_research_system_prompt,
    critique_agent_prompt,
    critique_agent_search_prompt,
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

_ACADEMIC_DB_TOOLS = {"eric_search", "openalex_search", "semantic_scholar_search", "arxiv_search", "elsevier_search", "scholar_search"}


class CritiqueDecision(BaseModel):
    decision: Literal["PASS", "NEEDS_WORK"]
    counter_claims: list[str] = Field(default_factory=list, description="3-5 specific counter-claims or contradictions found")
    gaps: list[str] = Field(default_factory=list, description="3-5 missing populations, outcomes, or methodological weaknesses")
    search_directive: str = Field(default="", description="Specific searches the researcher must run to address these counter-claims")


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

    # Enforce web search budget: drop tavily_search when limit is reached
    web_search_calls = state.get("web_search_calls", 0)
    max_web_searches = configurable.max_web_searches
    if max_web_searches is not None and web_search_calls >= max_web_searches:
        tools = [t for t in tools if (t.name if hasattr(t, "name") else t.get("name")) != "tavily_search"]

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

    # Build web search budget message for the prompt
    web_search_mode = configurable.web_search_mode
    if max_web_searches == 0:
        web_search_budget = (
            "**Web search unavailable** — use only academic databases "
            "(eric_search, openalex_search, semantic_scholar_search). Do not call tavily_search."
        )
    elif max_web_searches is None:
        web_search_budget = ""
    else:
        remaining = max(0, max_web_searches - web_search_calls)
        if remaining == 0:
            web_search_budget = (
                "**Web search budget: EXHAUSTED** — tavily_search is no longer available. "
                "Use only academic databases (eric_search, openalex_search, semantic_scholar_search)."
            )
        elif web_search_mode == "strategic":
            web_search_budget = (
                f"**Web search budget: {remaining} call(s) remaining** (used {web_search_calls} of {max_web_searches}). "
                "STRATEGIC USE ONLY — first exhaust academic databases (ERIC, OpenAlex, Semantic Scholar). "
                "Then assess what is genuinely missing and allocate remaining calls deliberately to: "
                "(1) academic literature not indexed in the DBs (preprints, conference papers, practitioner journals), "
                "(2) policy/grey literature (IES, What Works Clearinghouse, RAND, Brookings, College Board, ed.gov), "
                "or (3) very recent evidence (2024–2025) not yet indexed. "
                "Do not use a web search call unless you have identified a specific gap the academic DBs cannot fill."
            )
        else:
            web_search_budget = (
                f"**Web search budget: {remaining} call(s) remaining** (used {web_search_calls} of {max_web_searches})."
            )

    researcher_prompt = research_system_prompt.format(
        mcp_prompt=configurable.mcp_prompt or "",
        date=get_today_str(),
        web_search_budget=web_search_budget,
    )

    research_model = (
        configurable_model
        .bind_tools(tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )

    messages = [SystemMessage(content=researcher_prompt)] + researcher_messages
    response = await research_model.ainvoke(messages)

    # Capture agent reasoning for thought log
    text_content = ""
    if isinstance(response.content, str):
        text_content = response.content
    elif isinstance(response.content, list):
        text_content = " ".join(
            block.get("text", "") for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    tool_calls_made = [tc["name"] for tc in (response.tool_calls or [])]
    thought_entry = {
        "topic": research_topic,
        "iteration": state.get("tool_call_iterations", 0),
        "reasoning": text_content.strip(),
        "tools_called": tool_calls_made,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return Command(
        goto="researcher_tools",
        update={
            "researcher_messages": [response],
            "tool_call_iterations": state.get("tool_call_iterations", 0) + 1,
            "thought_log": [thought_entry],
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

    # Count calls per tool for source provenance tracking
    new_web_searches = 0
    new_source_counts: dict = {}
    for tc in tool_calls:
        name = tc["name"]
        if name == "tavily_search":
            new_web_searches += 1
            new_source_counts["tavily"] = new_source_counts.get("tavily", 0) + 1
        elif name in _ACADEMIC_DB_TOOLS:
            new_source_counts[name] = new_source_counts.get(name, 0) + 1

    updated_web_search_calls = state.get("web_search_calls", 0) + new_web_searches

    exceeded_iterations = state.get("tool_call_iterations", 0) >= configurable.max_react_tool_calls
    research_complete_called = any(
        tool_call["name"] == "ResearchComplete"
        for tool_call in most_recent_message.tool_calls
    )

    if exceeded_iterations or research_complete_called:
        return Command(
            goto="critique_agent",
            update={
                "researcher_messages": tool_outputs,
                "web_search_calls": updated_web_search_calls,
                "source_counts": new_source_counts,
            }
        )

    return Command(
        goto="researcher",
        update={
            "researcher_messages": tool_outputs,
            "web_search_calls": updated_web_search_calls,
            "source_counts": new_source_counts,
        }
    )


async def critique_agent(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher", "compress_research"]]:
    """Adversarial critique agent that searches for counter-claims and material gaps.

    Phase 1: Claude Sonnet with native Anthropic web search finds contradictory evidence.
    Phase 2: Claude Sonnet produces a structured CritiqueDecision with counter_claims/gaps.
    Hard cap of 2 critique cycles.
    """
    critique_cycles = state.get("critique_cycles", 0)

    if critique_cycles >= 2:
        return Command(goto="compress_research", update={})

    researcher_messages = state.get("researcher_messages", [])
    research_topic = state.get("research_topic", "")

    # Build findings summary from tool outputs — cap at 12k chars
    tool_outputs = [
        msg.content for msg in researcher_messages
        if hasattr(msg, "type") and msg.type == "tool"
    ]
    findings_summary = "\n\n".join(str(t) for t in tool_outputs)
    if len(findings_summary) > 12000:
        findings_summary = findings_summary[:12000] + "\n[truncated for brevity]"

    if not findings_summary.strip():
        return Command(goto="compress_research", update={})

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    try:
        # ── Phase 1: adversarial web search for counter-evidence ──────────────
        # Claude Sonnet handles web search server-side — one call, results baked into response
        search_prompt = critique_agent_search_prompt.format(
            research_topic=research_topic,
            findings_summary=findings_summary,
        )
        search_model = init_chat_model(
            model="anthropic:claude-sonnet-4-6",
            max_tokens=2048,
            api_key=anthropic_api_key,
            tags=["langsmith:nostream"],
        ).bind_tools([{"type": "web_search_20250305"}])

        search_response = await search_model.ainvoke([HumanMessage(content=search_prompt)])

        # Extract text — Anthropic embeds search results directly in the response content
        counter_evidence = ""
        if isinstance(search_response.content, str):
            counter_evidence = search_response.content
        elif isinstance(search_response.content, list):
            counter_evidence = " ".join(
                block.get("text", "") for block in search_response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        # ── Phase 2: structured adversarial critique decision ─────────────────
        counter_evidence_block = (
            f"<CounterEvidence>\n{counter_evidence.strip()}\n</CounterEvidence>"
            if counter_evidence.strip()
            else ""
        )
        decision_prompt = critique_agent_prompt.format(
            research_topic=research_topic,
            findings_summary=findings_summary,
            counter_evidence_block=counter_evidence_block,
        )
        decision_model = init_chat_model(
            model="anthropic:claude-sonnet-4-6",
            max_tokens=1024,
            api_key=anthropic_api_key,
            tags=["langsmith:nostream"],
        ).with_structured_output(CritiqueDecision)

        decision: CritiqueDecision = await decision_model.ainvoke([
            HumanMessage(content=decision_prompt)
        ])

    except Exception:
        return Command(goto="compress_research", update={})

    if decision.decision == "PASS":
        return Command(goto="compress_research", update={})

    # NEEDS_WORK — inject counter-claims so the researcher addresses them directly
    counter_claims_text = "\n".join(f"- {c}" for c in decision.counter_claims) or "None identified"
    gaps_text = "\n".join(f"- {g}" for g in decision.gaps) or "None identified"
    gap_message = HumanMessage(content=(
        f"ADVERSARIAL CRITIQUE (cycle {critique_cycles + 1}/2)\n\n"
        f"**Counter-claims you must address:**\n{counter_claims_text}\n\n"
        f"**Material gaps in the synthesis:**\n{gaps_text}\n\n"
        f"**Required follow-up searches:**\n{decision.search_directive}"
    ))
    return Command(
        goto="researcher",
        update={
            "researcher_messages": [gap_message],
            "critique_cycles": critique_cycles + 1,
            "tool_call_iterations": 0,
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
                "raw_notes": [raw_notes_content],
                "thought_log": state.get("thought_log", []),
                "source_counts": state.get("source_counts", {}),
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
        "raw_notes": [raw_notes_content],
        "thought_log": state.get("thought_log", []),
        "source_counts": state.get("source_counts", {}),
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

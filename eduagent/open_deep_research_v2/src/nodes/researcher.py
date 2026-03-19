"""Researcher subgraph — programmatic tier-based sweep, reflect, compress."""

import asyncio
import logging
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from configuration import Configuration
from prompts import (
    compress_research_prompt,
    compress_research_human,
    keyword_generation_prompt,
    researcher_reflect_prompt,
)
from state import KeywordSet, ReflectionDecision, ResearcherState
from utils.llm import get_model, get_today_str
from utils.paper_filter import relevance_filter, FILTERABLE_TOOLS
from utils.pdf_extractor import enrich_tool_output, PDF_EXTRACTABLE_TOOLS
from utils.search import get_all_tools, get_tools_by_name

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tier-based sweep plan
# Each entry: (tool_name, query_field) where query_field in {primary, variation, web}
# ---------------------------------------------------------------------------

SWEEP_BY_TIER: dict[str, list[tuple[str, str]]] = {
    "tier1": [
        ("semantic_scholar_search", "primary"),
        ("openai_web_search", "web"),
    ],
    "tier2": [
        ("semantic_scholar_search", "primary"),
        ("semantic_scholar_search", "variation"),
        ("openalex_search", "primary"),
        ("scholar_search", "variation"),
        ("openai_web_search", "web"),
    ],
    "tier3": [
        ("semantic_scholar_search", "primary"),
        ("semantic_scholar_search", "variation"),
        ("openalex_search", "primary"),
        ("scholar_search", "variation"),
        ("openai_web_search", "web"),
    ],
    "tier4": [
        ("semantic_scholar_search", "primary"),
        ("semantic_scholar_search", "variation"),
        ("eric_search", "primary"),
        ("eric_search", "variation"),
        ("openalex_search", "primary"),
        ("arxiv_search", "primary"),
        ("elsevier_search", "primary"),
        ("scholar_search", "variation"),
        ("tavily_search", "web"),
    ],
}

_QUERY_FIELD_MAP = {
    "primary": "primary_query",
    "variation": "variation_query",
    "web": "web_query",
}


# ---------------------------------------------------------------------------
# researcher node
# ---------------------------------------------------------------------------

async def researcher(state: ResearcherState, config: RunnableConfig) -> dict:
    """Generate keywords and execute programmatic tier sweep."""
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config)
    keyword_model = model.with_structured_output(KeywordSet).with_retry(stop_after_attempt=3)

    research_topic = state.get("research_topic", "")
    tier = state.get("tier", "tier3")
    current_keyword_set = state.get("current_keyword_set")

    # Reuse existing keyword set on re-sweeps (NEEDS_WORK cycle); generate fresh otherwise
    if current_keyword_set:
        kw = KeywordSet(**current_keyword_set)
    else:
        kw_prompt = keyword_generation_prompt.format(
            research_topic=research_topic,
            tier=tier,
            context=research_topic,
            date=get_today_str(),
        )
        kw = await keyword_model.ainvoke([HumanMessage(content=kw_prompt)])

    kw_dict = kw.model_dump()

    # Load tools
    all_tools = await get_all_tools(config)
    tools_by_name = get_tools_by_name(all_tools)

    sweep_plan = SWEEP_BY_TIER.get(tier, SWEEP_BY_TIER["tier3"])

    # Build async tasks for each (tool, query_field) pair
    async def run_sweep_entry(tool_name: str, query_field: str):
        tool = tools_by_name.get(tool_name)
        if tool is None:
            logger.debug(f"[researcher] Tool '{tool_name}' not available — skipping.")
            return tool_name, query_field, None

        attr = _QUERY_FIELD_MAP.get(query_field, "primary_query")
        query = kw_dict.get(attr, kw_dict.get("primary_query", ""))
        if not query:
            return tool_name, query_field, None

        try:
            # Each tool has its own required argument name
            if tool_name == "tavily_search":
                result = await tool.ainvoke({"queries": [query], "config": config})
            else:
                result = await tool.ainvoke({"query": query})

            if isinstance(result, list):
                result = "\n".join(str(r) for r in result)
            return tool_name, query_field, str(result)
        except Exception as e:
            logger.warning(f"[researcher] Tool '{tool_name}' failed: {e}")
            return tool_name, query_field, None

    tasks = [run_sweep_entry(tn, qf) for tn, qf in sweep_plan]
    raw_results = await asyncio.gather(*tasks)

    # Process results: filter + PDF extract
    source_counts: dict[str, int] = {}
    filter_log: list[dict] = []
    paper_profiles: list = []
    tool_messages: list[ToolMessage] = []

    for tool_name, query_field, raw_output in raw_results:
        if raw_output is None:
            continue

        output = raw_output

        # Relevance filter
        if tool_name in FILTERABLE_TOOLS:
            output, flog = await relevance_filter(
                tool_name=tool_name,
                tool_output=output,
                research_topic=research_topic,
                model_name=configurable.model,
            )
            filter_log.extend(flog)

        # PDF extraction
        if configurable.enable_pdf_extraction and tool_name in PDF_EXTRACTABLE_TOOLS:
            output, profiles = await enrich_tool_output(
                tool_name=tool_name,
                tool_output=output,
                research_topic=research_topic,
                model_name=configurable.model,
            )
            paper_profiles.extend(profiles)

        # Count sources
        source_counts[tool_name] = source_counts.get(tool_name, 0) + 1

        tool_messages.append(ToolMessage(
            content=output,
            name=tool_name,
            tool_call_id=f"{tool_name}_{query_field}_{state.get('sweep_cycles', 0)}",
        ))

    updates: dict = {
        "researcher_messages": tool_messages,
        "sweep_cycles": state.get("sweep_cycles", 0) + 1,
        "source_counts": source_counts,
        "filtered_papers_log": filter_log,
        "paper_profiles": paper_profiles,
        "keyword_history": [kw_dict],
        "current_keyword_set": kw_dict,
    }
    return updates


# ---------------------------------------------------------------------------
# researcher_reflect node
# ---------------------------------------------------------------------------

async def researcher_reflect(state: ResearcherState, config: RunnableConfig) -> dict:
    """Gap audit — decide PASS or NEEDS_WORK with targeted follow-up queries."""
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config).with_structured_output(ReflectionDecision).with_retry(stop_after_attempt=3)

    research_topic = state.get("research_topic", "")
    messages = state.get("researcher_messages", [])

    # Build a short summary of findings so far
    tool_outputs = [
        m.content for m in messages
        if isinstance(m, ToolMessage) and m.content and len(m.content) > 50
    ]
    findings_summary = "\n\n---\n\n".join(tool_outputs[-10:]) if tool_outputs else "No findings yet."

    prompt = researcher_reflect_prompt.format(
        research_topic=research_topic,
        findings_summary=findings_summary[:6000],
    )

    result: ReflectionDecision = await model.ainvoke([HumanMessage(content=prompt)])

    thought_entry = {
        "cycle": state.get("sweep_cycles", 0),
        "decision": result.decision,
        "gaps": result.gaps,
    }

    updates: dict = {
        "thought_log": [thought_entry],
    }

    if result.decision == "NEEDS_WORK":
        # Override current_keyword_set with targeted follow-up queries
        new_kw = {
            "primary_query": result.new_primary_query or state.get("current_keyword_set", {}).get("primary_query", ""),
            "variation_query": result.new_variation_query or state.get("current_keyword_set", {}).get("variation_query", ""),
            "web_query": result.new_web_query or state.get("current_keyword_set", {}).get("web_query", ""),
        }
        updates["current_keyword_set"] = new_kw

    return updates


# ---------------------------------------------------------------------------
# compress_research node
# ---------------------------------------------------------------------------

async def compress_research(state: ResearcherState, config: RunnableConfig) -> dict:
    """Synthesize all sweep ToolMessages into a single compressed research note."""
    model = get_model(config)

    messages = state.get("researcher_messages", [])
    research_topic = state.get("research_topic", "")

    # Collect all tool output strings
    findings_parts = []
    for m in messages:
        if isinstance(m, ToolMessage) and m.content:
            findings_parts.append(f"[{m.name}]\n{m.content}")

    findings_text = "\n\n---\n\n".join(findings_parts) if findings_parts else "No findings collected."

    system_prompt = compress_research_prompt.format(date=get_today_str())

    response = await model.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Research thread: {research_topic}\n\n{findings_text}"),
        HumanMessage(content=compress_research_human),
    ])

    compressed = str(response.content)

    # raw_notes = list of individual tool outputs (for the main graph aggregation)
    raw_outputs = [
        m.content for m in messages
        if isinstance(m, ToolMessage) and m.content
    ]

    return {
        "compressed_research": compressed,
        "raw_notes": {"type": "override", "value": raw_outputs},
    }


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_after_reflect(state: ResearcherState) -> Literal["researcher", "compress_research"]:
    """Loop back for another sweep cycle or proceed to compression."""
    configurable_max = 2  # default; can't easily access config in pure routing fn

    thought_log = state.get("thought_log", [])
    sweep_cycles = state.get("sweep_cycles", 0)

    if sweep_cycles >= configurable_max:
        return "compress_research"

    # Check last reflection decision
    for entry in reversed(thought_log):
        if "decision" in entry:
            if entry["decision"] == "NEEDS_WORK":
                return "researcher"
            return "compress_research"

    return "compress_research"


def route_after_reflect_with_config(max_cycles: int):
    """Factory: returns a routing function that respects max_sweep_cycles from config."""
    def _route(state: ResearcherState) -> Literal["researcher", "compress_research"]:
        sweep_cycles = state.get("sweep_cycles", 0)
        if sweep_cycles >= max_cycles:
            return "compress_research"

        thought_log = state.get("thought_log", [])
        for entry in reversed(thought_log):
            if "decision" in entry:
                if entry["decision"] == "NEEDS_WORK":
                    return "researcher"
                return "compress_research"

        return "compress_research"
    return _route


# ---------------------------------------------------------------------------
# Build researcher subgraph
# ---------------------------------------------------------------------------

_researcher_builder = StateGraph(ResearcherState)

_researcher_builder.add_node("researcher", researcher)
_researcher_builder.add_node("researcher_reflect", researcher_reflect)
_researcher_builder.add_node("compress_research", compress_research)

_researcher_builder.add_edge(START, "researcher")
_researcher_builder.add_edge("researcher", "researcher_reflect")
_researcher_builder.add_conditional_edges(
    "researcher_reflect",
    route_after_reflect,
    {"researcher": "researcher", "compress_research": "compress_research"},
)
_researcher_builder.add_edge("compress_research", END)

researcher_subgraph = _researcher_builder.compile()

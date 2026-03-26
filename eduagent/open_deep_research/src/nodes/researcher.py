"""Researcher nodes — keyword-set-driven parallel sweep across all academic DBs.

Architecture:
    researcher → researcher_reflect → (loop or compress_research) → END

Each researcher receives a sub-question from the supervisor, generates a KeywordSet
via one Haiku LLM call, then programmatically sweeps ALL configured academic DBs in
parallel (asyncio.gather). No LLM decides which tools to call — coverage is guaranteed.

researcher_reflect audits gaps and, if needed, generates a new KeywordSet for a
targeted follow-up sweep (max 2 sweeps total).
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Literal, Optional

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
    keyword_generation_prompt,
    researcher_reflect_prompt,
)
from state import ResearcherOutputState, ResearcherState
from utils.llm import (
    configurable_model,
    get_api_key_for_model,
    get_today_str,
    is_token_limit_exceeded,
    remove_up_to_last_ai_message,
)
from utils.search import get_all_tools
from utils.paper_filter import ensemble_filter, FILTERABLE_TOOLS
from utils.pdf_extractor import enrich_tool_output, PDF_EXTRACTABLE_TOOLS

# ── Sweep plan ─────────────────────────────────────────────────────────────────
# Each entry: (tool_name, query_field)
# query_field is one of "primary" | "variation" | "web"
# Tools absent from tools_by_name (not configured) are skipped silently.
_SWEEP_PLAN = [
    ("eric_search",                 "primary"),
    ("eric_search",                 "variation"),
    ("openalex_search",             "primary"),
    ("openalex_search",             "variation"),
    ("arxiv_search",                "primary"),
    ("elsevier_search",             "primary"),
    ("scholar_search",              "variation"),
    ("search_papers_by_relevance",  "primary"),
    ("search_papers_by_relevance",  "variation"),
    ("tavily_search",               "web"),
]

_ACADEMIC_DB_TOOLS = {
    "eric_search", "openalex_search", "semantic_scholar_search",
    "arxiv_search", "elsevier_search", "scholar_search",
    "search_papers_by_relevance", "snippet_search", "get_paper",
    "get_citations", "search_paper_by_title", "search_authors_by_name", "get_author_papers",
}


# ── Pydantic models ────────────────────────────────────────────────────────────

class KeywordSet(BaseModel):
    """Keyword set generated from a sub-question for DB sweeping."""
    primary_query: str = Field(
        description="Primary query for formal academic DBs — quoted phrases + academic signal words"
    )
    variation_query: str = Field(
        description="Variation using synonyms and different terminology"
    )
    web_query: str = Field(
        description="Natural language query for web/grey literature search"
    )


class ReflectionDecision(BaseModel):
    decision: Literal["PASS", "NEEDS_WORK"]
    gaps: list[str] = Field(default_factory=list, description="2-3 specific coverage gaps identified")
    new_primary_query: str = Field(default="", description="Follow-up academic DB query targeting the gaps")
    new_variation_query: str = Field(default="", description="Follow-up synonym/variation query")
    new_web_query: str = Field(default="", description="Follow-up web/grey literature query")


# ── Helpers ────────────────────────────────────────────────────────────────────

async def execute_tool_safely(tool, args, config):
    """Safely execute a tool with error handling."""
    try:
        return await tool.ainvoke(args, config)
    except Exception as e:
        return f"Error executing tool: {str(e)}"


async def _run_filter_and_extraction(
    call_specs: list[tuple[str, str]],
    raw_outputs: list[str],
    research_topic: str,
    configurable: Configuration,
    config: RunnableConfig,
) -> tuple[list[str], list[dict], list]:
    """Run ensemble filter then PDF extraction on sweep results.

    Returns: (final_outputs, filter_log, paper_profiles)
    """
    # Ensemble filter on academic DB results
    filter_tasks = [
        ensemble_filter(tool_name, output, research_topic)
        if tool_name in FILTERABLE_TOOLS and isinstance(output, str) and not output.startswith("Error:")
        else None
        for (tool_name, _), output in zip(call_specs, raw_outputs)
    ]
    filter_results_raw = await asyncio.gather(*[t for t in filter_tasks if t is not None])
    filter_iter = iter(filter_results_raw)
    filtered_outputs = []
    all_filter_log: list[dict] = []
    for i, task in enumerate(filter_tasks):
        if task is not None:
            filtered_output, log = next(filter_iter)
            filtered_outputs.append(filtered_output)
            all_filter_log.extend(log)
        else:
            filtered_outputs.append(raw_outputs[i])

    # PDF extraction
    all_paper_profiles = []
    if configurable.enable_pdf_extraction:
        extraction_tasks = [
            enrich_tool_output(tool_name, output, research_topic)
            if tool_name in PDF_EXTRACTABLE_TOOLS and isinstance(output, str) and not output.startswith("Error:")
            else None
            for (tool_name, _), output in zip(call_specs, filtered_outputs)
        ]
        extraction_results_raw = await asyncio.gather(
            *[t for t in extraction_tasks if t is not None],
            return_exceptions=True,
        )
        extraction_iter = iter(extraction_results_raw)
        final_outputs = []
        for i, task in enumerate(extraction_tasks):
            if task is not None:
                result = next(extraction_iter)
                if not isinstance(result, Exception):
                    enriched, profiles = result
                    final_outputs.append(enriched)
                    all_paper_profiles.extend(profiles)
                else:
                    final_outputs.append(filtered_outputs[i])
            else:
                final_outputs.append(filtered_outputs[i])
    else:
        final_outputs = filtered_outputs

    return final_outputs, all_filter_log, all_paper_profiles


# ── Researcher node ────────────────────────────────────────────────────────────

async def researcher(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher_reflect"]]:
    """Generate keyword set from sub-question, then sweep all DBs in parallel."""
    configurable = Configuration.from_runnable_config(config)
    research_topic = state.get("research_topic", "")
    sweep_cycles = state.get("sweep_cycles", 0)

    # ── Step 1: Get or generate keyword set ────────────────────────────────────
    current_keyword_set = state.get("current_keyword_set")
    if current_keyword_set:
        keyword_set = KeywordSet(**current_keyword_set)
    else:
        # Extract suggested keywords from the supervisor's HumanMessage brief
        messages = state.get("researcher_messages", [])
        raw_brief = ""
        if messages:
            first_msg = messages[0]
            raw_brief = first_msg.content if hasattr(first_msg, "content") else str(first_msg)

        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        try:
            keyword_model = init_chat_model(
                model="anthropic:claude-haiku-4-5-20251001",
                max_tokens=256,
                api_key=anthropic_api_key,
                tags=["langsmith:nostream"],
            ).with_structured_output(KeywordSet)

            kw_prompt = keyword_generation_prompt.format(
                sub_question=research_topic,
                suggested_keywords=raw_brief[:500],
                date=get_today_str(),
            )
            keyword_set = await keyword_model.ainvoke([HumanMessage(content=kw_prompt)])
        except Exception:
            # Fallback: use research_topic verbatim for all three queries
            keyword_set = KeywordSet(
                primary_query=research_topic,
                variation_query=research_topic,
                web_query=research_topic,
            )
        current_keyword_set = keyword_set.model_dump()

    # ── Step 2: Build sweep task list ──────────────────────────────────────────
    tools = await get_all_tools(config)
    tools_by_name = {
        (t.name if hasattr(t, "name") else t.get("name", "")): t
        for t in tools
    }

    web_search_calls = state.get("web_search_calls", 0)
    max_web_searches = configurable.max_web_searches

    query_map = {
        "primary":   keyword_set.primary_query,
        "variation": keyword_set.variation_query,
        "web":       keyword_set.web_query,
    }

    call_specs: list[tuple[str, str]] = []  # (tool_name, query)
    coros = []

    for tool_name, query_field in _SWEEP_PLAN:
        if tool_name not in tools_by_name:
            continue
        if tool_name == "tavily_search":
            if max_web_searches is not None and web_search_calls >= max_web_searches:
                continue
            args = {"queries": [query_map["web"]], "max_results": 10}
        else:
            args = {"query": query_map[query_field]}

        call_specs.append((tool_name, query_map[query_field]))
        coros.append(execute_tool_safely(tools_by_name[tool_name], args, config))

    # ── Step 3: Fire all DB calls in parallel ──────────────────────────────────
    raw_outputs = [str(r) for r in await asyncio.gather(*coros)]

    # ── Step 4: Filter + extract ───────────────────────────────────────────────
    final_outputs, all_filter_log, all_paper_profiles = await _run_filter_and_extraction(
        call_specs, raw_outputs, research_topic, configurable, config
    )

    # ── Step 5: Build ToolMessages for compress_research ──────────────────────
    tool_messages = []
    new_source_counts: dict = {}
    new_web_searches = 0

    for i, ((tool_name, query), output) in enumerate(zip(call_specs, final_outputs)):
        tool_messages.append(ToolMessage(
            content=f"[{tool_name} | query: {query}]\n{output}",
            name=tool_name,
            tool_call_id=f"sweep_{sweep_cycles}_{tool_name}_{i}",
        ))
        if tool_name == "tavily_search":
            new_web_searches += 1
            new_source_counts["tavily"] = new_source_counts.get("tavily", 0) + 1
        elif tool_name in _ACADEMIC_DB_TOOLS:
            new_source_counts[tool_name] = new_source_counts.get(tool_name, 0) + 1

    thought_entry = {
        "topic": research_topic,
        "iteration": sweep_cycles,
        "reasoning": (
            f"Sweep {sweep_cycles + 1} — "
            f"primary: '{keyword_set.primary_query}' | "
            f"variation: '{keyword_set.variation_query}' | "
            f"web: '{keyword_set.web_query}' | "
            f"tools fired: {[s[0] for s in call_specs]}"
        ),
        "tools_called": [s[0] for s in call_specs],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return Command(
        goto="researcher_reflect",
        update={
            "researcher_messages": tool_messages,
            "sweep_cycles": sweep_cycles + 1,
            "web_search_calls": web_search_calls + new_web_searches,
            "source_counts": new_source_counts,
            "filtered_papers_log": all_filter_log,
            "paper_profiles": all_paper_profiles,
            "thought_log": [thought_entry],
            "keyword_history": [current_keyword_set],
            "current_keyword_set": None,  # consumed; reflect sets it again if NEEDS_WORK
        }
    )


# ── Reflect node ───────────────────────────────────────────────────────────────

async def researcher_reflect(
    state: ResearcherState,
    config: RunnableConfig,
) -> Command[Literal["researcher", "compress_research"]]:
    """Gap audit — review sweep results, generate new keyword set if coverage insufficient.

    Hard cap: 2 sweeps total (sweep_cycles >= 2 → straight to compress_research).
    """
    sweep_cycles = state.get("sweep_cycles", 0)
    if sweep_cycles >= 2:
        return Command(goto="compress_research", update={})

    researcher_messages = state.get("researcher_messages", [])
    research_topic = state.get("research_topic", "")

    tool_outputs = [
        msg.content for msg in researcher_messages
        if hasattr(msg, "type") and msg.type == "tool"
    ]
    findings_summary = "\n\n".join(str(t) for t in tool_outputs)
    if len(findings_summary) > 8000:
        findings_summary = findings_summary[:8000] + "\n[truncated]"

    if not findings_summary.strip():
        return Command(goto="compress_research", update={})

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    try:
        reflect_model = init_chat_model(
            model="anthropic:claude-haiku-4-5-20251001",
            max_tokens=512,
            api_key=anthropic_api_key,
            tags=["langsmith:nostream"],
        ).with_structured_output(ReflectionDecision)

        reflect_prompt = researcher_reflect_prompt.format(
            research_topic=research_topic,
            findings_summary=findings_summary,
        )
        decision: ReflectionDecision = await reflect_model.ainvoke([
            HumanMessage(content=reflect_prompt)
        ])
    except Exception:
        return Command(goto="compress_research", update={})

    if decision.decision == "PASS" or not decision.new_primary_query:
        return Command(goto="compress_research", update={})

    # NEEDS_WORK — inject new keyword set for a targeted follow-up sweep
    new_keyword_set = {
        "primary_query":   decision.new_primary_query,
        "variation_query": decision.new_variation_query or decision.new_primary_query,
        "web_query":       decision.new_web_query or decision.new_primary_query,
    }
    return Command(
        goto="researcher",
        update={"current_keyword_set": new_keyword_set},
    )


# ── Compress node ──────────────────────────────────────────────────────────────

async def compress_research(state: ResearcherState, config: RunnableConfig):
    """Compress and synthesize all sweep findings into a structured research note."""
    configurable = Configuration.from_runnable_config(config)
    synthesizer_model = configurable_model.with_config({
        "model": configurable.compression_model,
        "max_tokens": configurable.compression_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.compression_model, config),
        "tags": ["langsmith:nostream"]
    })

    researcher_messages = state.get("researcher_messages", [])

    synthesis_attempts = 0
    max_attempts = 3

    while synthesis_attempts < max_attempts:
        try:
            compression_prompt = compress_research_system_prompt.format(date=get_today_str())

            def _msg_to_text(msg) -> str:
                content = msg.content
                if isinstance(content, list):
                    parts = []
                    for block in content:
                        if isinstance(block, str):
                            parts.append(block)
                        elif isinstance(block, dict):
                            if block.get("type") == "text":
                                parts.append(block.get("text", ""))
                            elif block.get("type") in ("function_call", "tool_use"):
                                name = block.get("name", "tool")
                                args = block.get("arguments") or block.get("input", "")
                                parts.append(f"[called {name}: {str(args)[:300]}]")
                    content = "\n".join(parts)
                return str(content)

            context_text = "\n\n".join(
                f"[{msg.__class__.__name__}]: {_msg_to_text(msg)}"
                for msg in researcher_messages
            )
            messages = [
                SystemMessage(content=compression_prompt),
                HumanMessage(content=f"{context_text}\n\n---\n\n{compress_research_simple_human_message}"),
            ]

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
                "filtered_papers_log": state.get("filtered_papers_log", []),
                "paper_profiles": state.get("paper_profiles", []),
            }

        except Exception as e:
            synthesis_attempts += 1
            import logging as _logging
            _logging.error(f"[compress_research] attempt {synthesis_attempts} failed: {type(e).__name__}: {e}")

            if is_token_limit_exceeded(e, configurable.compression_model):
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
        "filtered_papers_log": state.get("filtered_papers_log", []),
        "paper_profiles": state.get("paper_profiles", []),
    }


# ── Researcher subgraph ────────────────────────────────────────────────────────

researcher_builder = StateGraph(
    ResearcherState,
    output=ResearcherOutputState,
    config_schema=Configuration
)

researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_reflect", researcher_reflect)
researcher_builder.add_node("compress_research", compress_research)

researcher_builder.add_edge(START, "researcher")
researcher_builder.add_edge("compress_research", END)

researcher_subgraph = researcher_builder.compile()

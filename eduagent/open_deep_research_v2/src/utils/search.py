"""Web search tools — Tavily, OpenAI native web search, and tool registry."""

import asyncio
import logging
import os
from typing import Annotated, List, Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from tavily import AsyncTavilyClient


def get_tavily_api_key(config: RunnableConfig = None) -> str | None:
    should_get_from_config = os.getenv("GET_API_KEYS_FROM_CONFIG", "false")
    if should_get_from_config.lower() == "true":
        api_keys = (config or {}).get("configurable", {}).get("apiKeys", {})
        return api_keys.get("TAVILY_API_KEY")
    return os.getenv("TAVILY_API_KEY")


@tool(description=(
    "Targeted web retrieval for grey literature, policy reports, and specific known documents "
    "(IES, WWC, RAND, Brookings, ed.gov). Use for Tier 4 evidence gaps where academic DBs "
    "come up short. Always max_results=10. Requires TAVILY_API_KEY."
))
async def tavily_search(
    queries: List[str],
    max_results: Annotated[int, InjectedToolArg] = 10,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
    config: RunnableConfig = None,
) -> str:
    """Fetch search results from Tavily search API."""
    api_key = get_tavily_api_key(config)
    if not api_key:
        return "Tavily search: TAVILY_API_KEY not configured — skipping."

    client = AsyncTavilyClient(api_key=api_key)
    tasks = [
        client.search(q, max_results=max_results, include_raw_content=False, topic=topic)
        for q in queries
    ]

    try:
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        return f"Tavily search error: {e}"

    unique_results: dict[str, dict] = {}
    for response in responses:
        if isinstance(response, Exception):
            continue
        for result in response.get("results", []):
            url = result.get("url", "")
            if url and url not in unique_results:
                unique_results[url] = result

    if not unique_results:
        return "Tavily: No results found."

    lines = ["Tavily Web Search Results:\n"]
    for i, (url, result) in enumerate(unique_results.items(), 1):
        lines.append(f"--- SOURCE {i}: {result.get('title', 'No title')} ---")
        lines.append(f"URL: {url}")
        lines.append(f"Content: {result.get('content', '')}\n")

    return "\n".join(lines)


@tool(description=(
    "Search the web using OpenAI's native web search (GPT-powered). Use for broad academic "
    "coverage alongside the academic DBs — finding studies, grey literature, policy reports, "
    "and practitioner work. Best for Tier 1 and Tier 2 threads. Requires OPENAI_API_KEY."
))
async def openai_web_search(query: str) -> str:
    """Web search via OpenAI native search."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "OpenAI web search: OPENAI_API_KEY not configured."
    try:
        model = init_chat_model(
            model="openai:gpt-4.1-mini",
            max_tokens=2048,
            api_key=api_key,
            tags=["langsmith:nostream"],
        ).bind_tools([{"type": "web_search_preview"}])
        response = await model.ainvoke([HumanMessage(content=query)])
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            text_parts = [
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            return "\n".join(p for p in text_parts if p) or "No results returned."
        return "No results returned."
    except Exception as e:
        return f"OpenAI web search error: {e}"


async def load_asta_tools() -> list:
    """Load Asta (Allen AI) tools via MCP using ASTA_TOOL_KEY."""
    api_key = os.getenv("ASTA_TOOL_KEY", "")
    if not api_key:
        return []
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        client = MultiServerMCPClient({
            "asta": {
                "url": "https://asta-tools.allen.ai/mcp/v1",
                "headers": {"x-api-key": api_key},
                "transport": "streamable_http",
            }
        })
        tools = await client.get_tools()
        logging.info(f"[ASTA] Loaded {len(tools)} tools: {[t.name for t in tools]}")
        return tools
    except Exception as e:
        logging.warning(f"[ASTA] Could not load tools: {e}")
        return []


async def get_all_tools(config: RunnableConfig = None) -> list:
    """Assemble the complete toolkit for researchers."""
    from utils.llm import think_tool
    from utils.academic_search import (
        eric_search, openalex_search, arxiv_search, elsevier_search,
        scholar_search, semantic_scholar_search,
    )

    tools = [
        think_tool,
        openai_web_search,
        tavily_search,
        eric_search,
        openalex_search,
        arxiv_search,
        elsevier_search,
        scholar_search,
        semantic_scholar_search,
    ]

    # Load Asta (Allen AI) tools if key is available
    asta_tools = await load_asta_tools()
    if asta_tools:
        tools.extend(asta_tools)
        logging.info(f"[search] Added {len(asta_tools)} Asta tools")

    return tools


def get_tools_by_name(tools: list) -> dict:
    """Build a {name: tool} lookup from a tool list."""
    return {
        (t.name if hasattr(t, "name") else t.get("name", "")): t
        for t in tools
    }

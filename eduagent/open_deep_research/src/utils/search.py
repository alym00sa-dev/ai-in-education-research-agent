"""Search tools and web content retrieval utilities."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, tool
from tavily import AsyncTavilyClient

from configuration import Configuration, SearchAPI
from prompts import summarize_webpage_prompt
from state import Summary
from utils.llm import get_api_key_for_model, get_today_str
from utils.mcp import load_mcp_tools


def create_audit_log_file(query: str, audit_data: Dict[str, Any]) -> str:
    """Create an audit log file for Tavily search tracking.

    Args:
        query: The original research query
        audit_data: Dictionary containing all audit trail information

    Returns:
        Path to the created audit log file
    """
    audit_dir = Path("audit_logs")
    audit_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"audit_{timestamp}.json"
    filepath = audit_dir / filename

    audit_log = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "audit_trail": audit_data
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(audit_log, f, indent=2, ensure_ascii=False)

    logging.info(f"[TAVILY AUDIT] Audit log saved to: {filepath}")
    return str(filepath)


async def summarize_webpage(model: BaseChatModel, webpage_content: str) -> str:
    """Summarize webpage content using AI model with timeout protection.

    Args:
        model: The chat model configured for summarization
        webpage_content: Raw webpage content to be summarized

    Returns:
        Formatted summary with key excerpts, or original content if summarization fails
    """
    try:
        prompt_content = summarize_webpage_prompt.format(
            webpage_content=webpage_content,
            date=get_today_str()
        )

        summary = await asyncio.wait_for(
            model.ainvoke([HumanMessage(content=prompt_content)]),
            timeout=60.0
        )

        return (
            f"<summary>\n{summary.summary}\n</summary>\n\n"
            f"<key_excerpts>\n{summary.key_excerpts}\n</key_excerpts>"
        )

    except asyncio.TimeoutError:
        logging.warning("Summarization timed out after 60 seconds, returning original content")
        return webpage_content
    except Exception as e:
        logging.warning(f"Summarization failed with error: {str(e)}, returning original content")
        return webpage_content


def get_config_value(value):
    """Extract value from configuration, handling enums and None values."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return value
    else:
        return value.value


def get_tavily_api_key(config: RunnableConfig):
    """Get Tavily API key from environment or config."""
    import os
    should_get_from_config = os.getenv("GET_API_KEYS_FROM_CONFIG", "false")
    if should_get_from_config.lower() == "true":
        api_keys = config.get("configurable", {}).get("apiKeys", {})
        if not api_keys:
            return None
        return api_keys.get("TAVILY_API_KEY")
    else:
        return os.getenv("TAVILY_API_KEY")


TAVILY_SEARCH_DESCRIPTION = (
    "Targeted web retrieval for specific known documents. Use ONLY when you have a specific "
    "named study, paper, or policy document (IES, WWC, RAND, Brookings, ed.gov) that you know "
    "exists and need to retrieve. Not for general topic sweeps — use anthropic_web_search or "
    "openai_web_search for broad coverage instead. Check your remaining budget before calling."
)


@tool(description=TAVILY_SEARCH_DESCRIPTION)
async def tavily_search(
    queries: List[str],
    max_results: Annotated[int, InjectedToolArg] = 5,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
    config: RunnableConfig = None
) -> str:
    """Fetch and summarize search results from Tavily search API.

    Args:
        queries: List of search queries to execute
        max_results: Maximum number of results to return per query
        topic: Topic filter for search results (general, news, or finance)
        config: Runtime configuration for API keys and model settings

    Returns:
        Formatted string containing summarized search results
    """
    audit_data = {
        "queries": queries,
        "max_results_per_query": max_results,
        "topic": topic,
        "tavily_raw_results": [],
        "deduplication": {},
        "summarization": {},
        "final_sources": []
    }

    logging.info(f"[TAVILY AUDIT] Starting Tavily search with {len(queries)} queries")
    logging.info(f"[TAVILY AUDIT] Queries: {queries}")
    logging.info(f"[TAVILY AUDIT] Max results per query: {max_results}, Topic: {topic}")

    search_results = await tavily_search_async(
        queries,
        max_results=max_results,
        topic=topic,
        include_raw_content=True,
        config=config
    )

    total_results = sum(len(response.get('results', [])) for response in search_results)
    logging.info(f"[TAVILY AUDIT] Tavily returned {total_results} total results across all queries")

    for response in search_results:
        query_results = {
            "query": response.get('query', 'unknown'),
            "results": [
                {
                    "title": r.get('title', 'No title'),
                    "url": r['url'],
                    "score": r.get('score', None),
                    "content_preview": r.get('content', '')[:200]
                }
                for r in response.get('results', [])
            ]
        }
        audit_data["tavily_raw_results"].append(query_results)

    unique_results = {}
    duplicate_count = 0
    duplicates = []

    for response in search_results:
        query = response.get('query', 'unknown')
        logging.info(f"[TAVILY AUDIT] Processing results for query: '{query}'")

        for i, result in enumerate(response['results'], 1):
            url = result['url']
            title = result.get('title', 'No title')
            score = result.get('score', 'N/A')

            if url not in unique_results:
                unique_results[url] = {**result, "query": response['query']}
                logging.info(f"[TAVILY AUDIT]   Source {i}: {title}")
                logging.info(f"[TAVILY AUDIT]   URL: {url}")
                logging.info(f"[TAVILY AUDIT]   Relevance Score: {score}")
            else:
                duplicate_count += 1
                duplicates.append({"url": url, "title": title})
                logging.info(f"[TAVILY AUDIT]   DUPLICATE SKIPPED: {url}")

    audit_data["deduplication"] = {
        "total_before": total_results,
        "unique_after": len(unique_results),
        "duplicates_removed": duplicate_count,
        "duplicate_urls": duplicates
    }

    logging.info(
        f"[TAVILY AUDIT] After deduplication: {len(unique_results)} unique sources "
        f"({duplicate_count} duplicates removed)"
    )

    configurable = Configuration.from_runnable_config(config)
    max_char_to_include = configurable.max_content_length

    model_api_key = get_api_key_for_model(configurable.summarization_model, config)
    summarization_model = init_chat_model(
        model=configurable.summarization_model,
        max_tokens=configurable.summarization_model_max_tokens,
        api_key=model_api_key,
        tags=["langsmith:nostream"]
    ).with_structured_output(Summary).with_retry(
        stop_after_attempt=configurable.max_structured_output_retries
    )

    async def noop():
        return None

    logging.info(f"[TAVILY AUDIT] Starting summarization with model: {configurable.summarization_model}")
    logging.info(f"[TAVILY AUDIT] Max content length per source: {max_char_to_include} characters")

    summarization_tasks = [
        noop() if not result.get("raw_content")
        else summarize_webpage(
            summarization_model,
            result['raw_content'][:max_char_to_include]
        )
        for result in unique_results.values()
    ]

    summaries = await asyncio.gather(*summarization_tasks)

    successful_summaries = sum(1 for s in summaries if s is not None)
    failed_summaries = len(summaries) - successful_summaries
    logging.info(
        f"[TAVILY AUDIT] Summarization complete: {successful_summaries} successful, "
        f"{failed_summaries} skipped/failed"
    )

    audit_data["summarization"] = {
        "model": configurable.summarization_model,
        "max_content_length": max_char_to_include,
        "successful": successful_summaries,
        "failed": failed_summaries,
        "total_attempted": len(summaries)
    }

    summarized_results = {
        url: {
            'title': result['title'],
            'content': result['content'] if summary is None else summary
        }
        for url, result, summary in zip(
            unique_results.keys(),
            unique_results.values(),
            summaries
        )
    }

    if not summarized_results:
        logging.warning("[TAVILY AUDIT] No valid search results found")
        return "No valid search results found. Please try different search queries or use a different search API."

    logging.info("[TAVILY AUDIT] ========== FINAL SOURCE LIST ==========")
    for i, (url, result) in enumerate(summarized_results.items(), 1):
        logging.info(f"[TAVILY AUDIT] Final Source {i}: {result['title']}")
        logging.info(f"[TAVILY AUDIT]   URL: {url}")
        summary_preview = result['content'][:100] if isinstance(result['content'], str) else str(result['content'])[:100]
        logging.info(f"[TAVILY AUDIT]   Summary preview: {summary_preview}...")

        audit_data["final_sources"].append({
            "source_number": i,
            "title": result['title'],
            "url": url,
            "summary_preview": summary_preview,
            "summary_full": result['content'] if isinstance(result['content'], str) else str(result['content'])
        })

    logging.info("[TAVILY AUDIT] ========================================")
    logging.info(f"[TAVILY AUDIT] Total sources included in research: {len(summarized_results)}")

    main_query = queries[0] if queries else "unknown_query"
    try:
        audit_filepath = create_audit_log_file(main_query, audit_data)
        logging.info(f"[TAVILY AUDIT] Audit trail saved successfully to {audit_filepath}")
    except Exception as e:
        logging.error(f"[TAVILY AUDIT] Failed to save audit log: {e}")

    formatted_output = "Search results: \n\n"
    for i, (url, result) in enumerate(summarized_results.items()):
        formatted_output += f"\n\n--- SOURCE {i+1}: {result['title']} ---\n"
        formatted_output += f"URL: {url}\n\n"
        formatted_output += f"SUMMARY:\n{result['content']}\n\n"
        formatted_output += "\n\n" + "-" * 80 + "\n"

    return formatted_output


async def tavily_search_async(
    search_queries,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = True,
    config: RunnableConfig = None
):
    """Execute multiple Tavily search queries asynchronously.

    Args:
        search_queries: List of search query strings to execute
        max_results: Maximum number of results per query
        topic: Topic category for filtering results
        include_raw_content: Whether to include full webpage content
        config: Runtime configuration for API key access

    Returns:
        List of search result dictionaries from Tavily API
    """
    tavily_client = AsyncTavilyClient(api_key=get_tavily_api_key(config))

    search_tasks = [
        tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic
        )
        for query in search_queries
    ]

    return await asyncio.gather(*search_tasks)


@tool(description=(
    "Search the web using Anthropic's native web search (Claude-powered). "
    "Use for broad academic coverage alongside the academic DBs — finding studies, evidence, "
    "and literature on the topic even without a specific paper in mind. Surfaces grey literature, "
    "policy reports, practitioner work, and web-indexed studies that DBs may miss. "
    "Requires ANTHROPIC_API_KEY."
))
async def anthropic_web_search(query: str) -> str:
    """Web search via Anthropic native search (claude-haiku-4-5-20251001)."""
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "Anthropic web search: ANTHROPIC_API_KEY not configured."
    try:
        model = init_chat_model(
            model="anthropic:claude-haiku-4-5-20251001",
            max_tokens=2048,
            api_key=api_key,
            tags=["langsmith:nostream"],
        ).bind_tools([{"type": "web_search_20250305", "name": "web_search"}])
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
        return f"Anthropic web search error: {e}"


@tool(description=(
    "Search the web using OpenAI's native web search (GPT-powered). "
    "Use for broad academic coverage alongside the academic DBs — finding studies, evidence, "
    "and literature on the topic even without a specific paper in mind. Surfaces grey literature, "
    "policy reports, practitioner work, and web-indexed studies that DBs may miss. "
    "Requires OPENAI_API_KEY."
))
async def openai_web_search(query: str) -> str:
    """Web search via OpenAI native search (gpt-4.1-mini)."""
    import os
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


async def get_search_tool(search_api: SearchAPI):
    """Configure and return search tools based on the specified API provider.

    Args:
        search_api: The search API provider to use (Anthropic, OpenAI, Tavily, or None)

    Returns:
        List of configured search tool objects for the specified provider
    """
    if search_api == SearchAPI.ANTHROPIC:
        return [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    elif search_api == SearchAPI.OPENAI:
        return [{"type": "web_search_preview"}]

    elif search_api == SearchAPI.TAVILY:
        search_tool = tavily_search
        search_tool.metadata = {
            **(search_tool.metadata or {}),
            "type": "search",
            "name": "web_search"
        }
        return [search_tool]

    elif search_api == SearchAPI.NONE:
        return []

    return []


async def load_asta_tools() -> list:
    """Load all available Asta tools via MCP using the ASTA_TOOL_KEY.

    Connects to https://asta-tools.allen.ai/mcp/v1 and returns all tools
    Allen AI exposes (search_papers_by_relevance, snippet_search, get_paper,
    get_citations, search_paper_by_title, search_authors_by_name, get_author_papers).

    Returns empty list if key is missing or connection fails — never raises.
    """
    import os
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


async def get_all_tools(config: RunnableConfig):
    """Assemble complete toolkit including research, search, and MCP tools.

    Args:
        config: Runtime configuration specifying search API and MCP settings

    Returns:
        List of all configured and available tools for research operations
    """
    from utils.llm import think_tool
    from state import ResearchComplete
    from langchain_core.tools import tool as lc_tool

    tools = [lc_tool(ResearchComplete), think_tool]

    configurable = Configuration.from_runnable_config(config)
    search_api = SearchAPI(get_config_value(configurable.search_api))
    search_tools = await get_search_tool(search_api)
    tools.extend(search_tools)

    # Academic database tools
    from utils.academic_search import eric_search, openalex_search, arxiv_search, elsevier_search, scholar_search
    tools.extend([eric_search, openalex_search, arxiv_search, elsevier_search, scholar_search])
    # semantic_scholar_search commented out — API key pending activation

    # Native web search wrappers (always available regardless of search_api setting)
    tools.extend([anthropic_web_search, openai_web_search])

    # Asta scientific corpus tools (Allen AI) — loaded via MCP if ASTA_TOOL_KEY is set
    asta_tools = await load_asta_tools()
    tools.extend(asta_tools)

    existing_tool_names = {
        t.name if hasattr(t, "name") else t.get("name", "web_search")
        for t in tools
    }

    mcp_tools = await load_mcp_tools(config, existing_tool_names)
    tools.extend(mcp_tools)

    return tools

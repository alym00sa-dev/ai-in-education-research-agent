"""Claude web search via Anthropic's built-in web_search tool."""
import os
import time
from typing import List

import anthropic

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    start = time.time()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search for research on: {query}\n\n"
                    "Find academic papers, studies, and credible sources. "
                    "List the most relevant results with their titles and URLs."
                ),
            }],
        )
        latency = time.time() - start

        results: List[SearchResult] = []
        llm_answer = ""

        for block in response.content:
            if block.type == "text":
                llm_answer += block.text
            # Extract cited sources from web search result blocks
            elif hasattr(block, "type") and block.type == "tool_result":
                pass

        # Parse cited sources from the answer text — Claude inline-cites with URLs
        import re
        urls_seen = set()
        # Extract from citation footnotes like [Title](url) or raw URLs
        for match in re.finditer(r'\[([^\]]+)\]\((https?://[^\)]+)\)', llm_answer):
            title, url = match.group(1), match.group(2)
            if url not in urls_seen:
                urls_seen.add(url)
                results.append(SearchResult(title=title, url=url, snippet=""))

        # Also grab any bare URLs not already captured
        for url in re.findall(r'https?://[^\s\)\]"\']+', llm_answer):
            if url not in urls_seen:
                urls_seen.add(url)
                results.append(SearchResult(title=url.split("/")[-1] or url, url=url, snippet=""))

        return SearchResponse(
            searcher="claude",
            query=query,
            results=results[:num_results],
            latency_s=round(latency, 2),
            llm_answer=llm_answer,
        )
    except Exception as e:
        return SearchResponse(
            searcher="claude",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

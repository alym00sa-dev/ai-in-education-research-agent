"""Tavily search API."""
import os
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    api_key = os.environ["TAVILY_API_KEY"]
    start = time.time()
    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": num_results,
                "include_raw_content": False,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        data = response.json()
        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("content", ""),
            )
            for r in data.get("results", [])
        ]
        return SearchResponse(
            searcher="tavily",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="tavily",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

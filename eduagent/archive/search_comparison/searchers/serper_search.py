"""Serper (Google Search) API."""
import os
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    api_key = os.environ["SERPER_API_KEY"]
    start = time.time()
    try:
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num_results},
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        data = response.json()
        organic = data.get("organic", [])

        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("link", ""),
                snippet=r.get("snippet", ""),
            )
            for r in organic
        ]
        return SearchResponse(
            searcher="serper",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="serper",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

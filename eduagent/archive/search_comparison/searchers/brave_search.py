"""Brave Search API."""
import os
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    api_key = os.environ["BRAVE_API_KEY"]
    start = time.time()
    try:
        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "X-Subscription-Token": api_key,
                "Accept": "application/json",
            },
            params={"q": query, "count": num_results, "search_lang": "en"},
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        data = response.json()
        web_results = data.get("web", {}).get("results", [])

        results = [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("description", ""),
            )
            for r in web_results
        ]
        return SearchResponse(
            searcher="brave",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="brave",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

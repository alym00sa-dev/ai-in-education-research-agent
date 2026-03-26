"""Exa semantic search."""
import os
import time

from exa_py import Exa

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    client = Exa(api_key=os.environ["EXA_API_KEY"])
    start = time.time()
    try:
        response = client.search_and_contents(
            query,
            num_results=num_results,
            text={"max_characters": 500},
        )
        latency = time.time() - start

        results = [
            SearchResult(
                title=r.title or r.url,
                url=r.url,
                snippet=r.text or "",
            )
            for r in response.results
        ]
        return SearchResponse(
            searcher="exa",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="exa",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

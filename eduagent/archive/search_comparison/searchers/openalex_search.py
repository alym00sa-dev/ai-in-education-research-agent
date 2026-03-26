"""OpenAlex academic paper search — free, no API key required."""
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    start = time.time()
    try:
        response = httpx.get(
            "https://api.openalex.org/works",
            params={
                "search": query,
                "per-page": num_results,
                "select": "id,title,doi,primary_location,abstract_inverted_index,publication_year,cited_by_count,open_access",
                "sort": "relevance_score:desc",
                "filter": "primary_topic.field.id:33",  # 33 = Education field in OpenAlex
                "mailto": "research@eduagent.ai",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        results = []
        for work in response.json().get("results", []):
            title = work.get("title", "") or ""
            doi = work.get("doi", "") or ""
            year = work.get("publication_year", "")
            cited_by = work.get("cited_by_count", 0)

            # Best URL: DOI > landing page > OA URL
            loc = work.get("primary_location") or {}
            url = doi or loc.get("landing_page_url", "") or loc.get("pdf_url", "") or ""

            # Reconstruct abstract from inverted index
            inv = work.get("abstract_inverted_index") or {}
            snippet = ""
            if inv:
                words = [""] * (max(max(v) for v in inv.values()) + 1)
                for word, positions in inv.items():
                    for pos in positions:
                        words[pos] = word
                snippet = " ".join(words)[:500]

            meta = f"[{year}] Cited by {cited_by}"
            results.append(SearchResult(
                title=f"{title} {meta}",
                url=url,
                snippet=snippet,
            ))

        return SearchResponse(
            searcher="openalex",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="openalex",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

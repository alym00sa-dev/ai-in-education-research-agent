"""Semantic Scholar (AI2) search — free, no API key required for basic use."""
import os
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    start = time.time()
    headers = {"User-Agent": "EduResearchAgent/1.0"}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    if api_key:
        headers["x-api-key"] = api_key

    try:
        response = httpx.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            headers=headers,
            params={
                "query": query,
                "limit": num_results,
                "fields": "title,abstract,year,citationCount,externalIds,openAccessPdf,publicationVenue,tldr",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        results = []
        for paper in response.json().get("data", []):
            title = paper.get("title", "") or ""
            abstract = paper.get("abstract", "") or ""
            year = paper.get("year", "")
            citations = paper.get("citationCount", 0)
            tldr = (paper.get("tldr") or {}).get("text", "")
            venue = (paper.get("publicationVenue") or {}).get("name", "")

            # Best URL: DOI > open access PDF > S2 page
            ext_ids = paper.get("externalIds") or {}
            doi = ext_ids.get("DOI", "")
            oa_pdf = (paper.get("openAccessPdf") or {}).get("url", "")
            paper_id = paper.get("paperId", "")
            url = (f"https://doi.org/{doi}" if doi else
                   oa_pdf or
                   f"https://www.semanticscholar.org/paper/{paper_id}")

            # Prefer TLDR > abstract for snippet
            snippet = tldr or abstract[:500]
            meta = f"[{year}] Cited by {citations}" + (f" | {venue}" if venue else "")

            results.append(SearchResult(
                title=f"{title} {meta}",
                url=url,
                snippet=snippet,
            ))

        return SearchResponse(
            searcher="semantic_scholar",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="semantic_scholar",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

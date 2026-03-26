"""ERIC (Education Resources Information Center) search — free, no API key required."""
import time

import httpx

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    start = time.time()
    try:
        response = httpx.get(
            "https://api.ies.ed.gov/eric/",
            params={
                "search": query,
                "format": "json",
                "rows": num_results,
                "fields": "id,title,description,subject,publicationdateyear,source,url,peerreviewed,educationlevel",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        latency = time.time() - start

        data = response.json()
        docs = data.get("response", {}).get("docs", [])

        results = []
        for doc in docs:
            title = doc.get("title", "") or ""
            description = doc.get("description", "") or ""
            year = doc.get("publicationdateyear", "")
            source = doc.get("source", "")
            peer = "Peer-reviewed" if doc.get("peerreviewed") == "T" else ""
            ed_level = ", ".join(doc.get("educationlevel", []) or [])
            eric_id = doc.get("id", "")

            url = doc.get("url", "") or (f"https://eric.ed.gov/?id={eric_id}" if eric_id else "")
            meta_parts = [p for p in [str(year), source, peer, ed_level] if p]
            snippet = description[:500] if description else ""

            results.append(SearchResult(
                title=f"{title} [{', '.join(meta_parts)}]",
                url=url,
                snippet=snippet,
            ))

        return SearchResponse(
            searcher="eric",
            query=query,
            results=results,
            latency_s=round(latency, 2),
        )
    except Exception as e:
        return SearchResponse(
            searcher="eric",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

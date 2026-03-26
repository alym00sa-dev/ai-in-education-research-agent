"""OpenAI web search via gpt-4o-search-preview."""
import os
import re
import time
from typing import List

from openai import OpenAI

from .base import SearchResponse, SearchResult


def search(query: str, num_results: int = 10) -> SearchResponse:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    start = time.time()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
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

        answer = response.choices[0].message.content or ""
        results: List[SearchResult] = []

        # Extract citations from annotations if present
        annotations = getattr(response.choices[0].message, "annotations", None) or []
        urls_seen = set()

        for ann in annotations:
            url = getattr(ann, "url", None) or getattr(getattr(ann, "url_citation", None), "url", None) or ""
            title = getattr(ann, "title", None) or getattr(getattr(ann, "url_citation", None), "title", None) or url
            if url and url not in urls_seen:
                urls_seen.add(url)
                results.append(SearchResult(title=title, url=url, snippet=""))

        # Fallback: parse markdown links from the answer
        if not results:
            for match in re.finditer(r'\[([^\]]+)\]\((https?://[^\)]+)\)', answer):
                title, url = match.group(1), match.group(2)
                if url not in urls_seen:
                    urls_seen.add(url)
                    results.append(SearchResult(title=title, url=url, snippet=""))

        return SearchResponse(
            searcher="openai",
            query=query,
            results=results[:num_results],
            latency_s=round(latency, 2),
            llm_answer=answer,
        )
    except Exception as e:
        return SearchResponse(
            searcher="openai",
            query=query,
            latency_s=round(time.time() - start, 2),
            error=str(e),
        )

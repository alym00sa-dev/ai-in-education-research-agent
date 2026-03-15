"""Academic database search tools — ERIC, Semantic Scholar, OpenAlex.

Each tool is a LangChain @tool-decorated async function that sub-researchers
can call alongside web search. All three:
  - Accept a plain query string
  - Apply a relevance filter (keyword overlap against title + abstract)
  - Return a uniform formatted block per result, including PDF links where available
  - Handle HTTP errors gracefully (return an error note rather than raising)
"""

import asyncio
import os
import re
from typing import List

import httpx
from langchain_core.tools import tool


# ── Shared utilities ──────────────────────────────────────────────────────────

_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "to", "for", "with", "on",
    "at", "from", "by", "about", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "that", "this", "these",
    "those", "its", "it", "i", "we", "they", "their", "our", "how", "what",
    "which", "when", "where", "who", "not", "no", "if", "but", "so", "than",
}

_TIMEOUT = httpx.Timeout(30.0)
_ERIC_TIMEOUT = httpx.Timeout(45.0)  # ERIC API is slow
_HEADERS = {"User-Agent": "EduResearchAgent/1.0 (academic research tool; contact research@edu-tool)"}


def _relevance_score(query: str, title: str, abstract: str) -> int:
    """Count how many non-trivial query tokens appear in title + abstract."""
    tokens = {
        w.lower() for w in re.findall(r"\w+", query)
        if w.lower() not in _STOPWORDS and len(w) > 2
    }
    if not tokens:
        return 1  # nothing to filter on — keep everything
    haystack = (title + " " + abstract).lower()
    return sum(1 for t in tokens if t in haystack)


def _filter_and_rank(results: List[dict], query: str, top_n: int = 10) -> List[dict]:
    """Drop low-relevance results and return top_n sorted by descending score.

    Two-gate filter:
      1. Title gate — at least 1 query keyword must appear in the title.
         This eliminates off-domain papers (e.g. medical journals) that only
         match on generic words like "learning" or "outcomes" in their abstracts.
      2. Score gate — combined title+abstract score must meet a minimum that
         scales with query length (≥2 for long queries, ≥1 for short ones).
    """
    tokens = {
        w.lower() for w in re.findall(r"\w+", query)
        if w.lower() not in _STOPWORDS and len(w) > 2
    }
    if not tokens:
        return results[:top_n]

    min_score = 2 if len(tokens) >= 4 else 1

    def title_matches(title: str) -> bool:
        t = title.lower()
        return any(tok in t for tok in tokens)

    scored = [
        (r, _relevance_score(query, r.get("title", ""), r.get("abstract", "")))
        for r in results
    ]
    relevant = [
        (r, s) for r, s in scored
        if s >= min_score and title_matches(r.get("title", ""))
    ]
    relevant.sort(key=lambda x: x[1], reverse=True)
    return [r for r, _ in relevant[:top_n]]


def _format_result(idx: int, title: str, authors: str, year: str,
                   source_id: str, abstract: str, url: str, pdf_url: str) -> str:
    lines = [
        f"[{idx}] Title: {title}",
        f"    Authors: {authors} ({year})" if authors else f"    Year: {year}",
        f"    Source: {source_id}",
    ]
    if abstract:
        trimmed = abstract[:400] + "..." if len(abstract) > 400 else abstract
        lines.append(f"    Abstract: {trimmed}")
    if pdf_url:
        lines.append(f"    PDF: {pdf_url}")
    if url:
        lines.append(f"    URL: {url}")
    return "\n".join(lines)


# ── ERIC ──────────────────────────────────────────────────────────────────────

@tool(description=(
    "Search the ERIC (Education Resources Information Center) database for peer-reviewed "
    "education research, journal articles, and reports. Best for: K-12 education, higher "
    "education, tutoring, learning interventions, curriculum, and US education policy. "
    "Returns structured results with abstracts and PDF links where available."
))
async def eric_search(query: str) -> str:
    """Search ERIC for education literature matching the query."""
    params = {
        "search": query,
        "fields": "title,author,publicationdateyear,description,url,pdfurl,id",
        "format": "json",
        "rows": 15,
    }
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=_ERIC_TIMEOUT, headers=_HEADERS) as client:
                resp = await client.get("https://api.ies.ed.gov/eric/", params=params)
                if resp.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
        except httpx.TimeoutException:
            if attempt == 2:
                return "ERIC search error: request timed out after 3 attempts"
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            return f"ERIC search error: {e}"
    else:
        return "ERIC search error: server error after 3 attempts (API may be temporarily unavailable)"

    docs = (data.get("response") or {}).get("docs") or []
    if not docs:
        return "ERIC: No results found."

    raw = []
    for d in docs:
        raw.append({
            "title": d.get("title", ""),
            "abstract": d.get("description", ""),
            "authors": ", ".join(d.get("author", []) or []),
            "year": str(d.get("publicationdateyear", "") or ""),
            "url": d.get("url", "") or f"https://eric.ed.gov/?id={d.get('id', '')}",
            "pdf_url": d.get("pdfurl", "") or "",
            "source_id": f"ERIC / {d.get('id', '')}",
        })

    filtered = _filter_and_rank(raw, query)
    if not filtered:
        return "ERIC: No sufficiently relevant results found for this query."

    blocks = [
        _format_result(
            i + 1,
            r["title"], r["authors"], r["year"],
            r["source_id"], r["abstract"], r["url"], r["pdf_url"],
        )
        for i, r in enumerate(filtered)
    ]
    return f"ERIC Search Results ({len(filtered)} relevant):\n\n" + "\n\n".join(blocks)


# ── Semantic Scholar ──────────────────────────────────────────────────────────

@tool(description=(
    "Search Semantic Scholar for academic papers across all disciplines, with strong "
    "coverage of education technology, learning sciences, cognitive science, and AI. "
    "Returns citation-rich results with abstracts and open-access PDF links where available. "
    "Use for: empirical studies, meta-analyses, and cross-disciplinary education research."
))
async def semantic_scholar_search(query: str) -> str:
    """Search Semantic Scholar for academic papers matching the query."""
    params = {
        "query": query,
        "fields": "title,authors,year,abstract,openAccessPdf,externalIds,url",
        "limit": 15,
    }
    ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    ss_headers = {**_HEADERS, **({"x-api-key": ss_api_key} if ss_api_key else {})}

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT, headers=ss_headers) as client:
                resp = await client.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params=params,
                )
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
        except Exception as e:
            if attempt == 2:
                return f"Semantic Scholar search error: {e}"
            await asyncio.sleep(2 ** attempt)
    else:
        return "Semantic Scholar search error: rate limited after 3 attempts"

    papers = data.get("data") or []
    if not papers:
        return "Semantic Scholar: No results found."

    raw = []
    for p in papers:
        doi = (p.get("externalIds") or {}).get("DOI", "")
        url = p.get("url", "") or (f"https://doi.org/{doi}" if doi else "")
        pdf_url = (p.get("openAccessPdf") or {}).get("url", "") or ""
        authors_list = p.get("authors") or []
        authors_str = ", ".join(a.get("name", "") for a in authors_list[:3])
        if len(authors_list) > 3:
            authors_str += " et al."
        raw.append({
            "title": p.get("title", ""),
            "abstract": p.get("abstract", "") or "",
            "authors": authors_str,
            "year": str(p.get("year", "") or ""),
            "url": url,
            "pdf_url": pdf_url,
            "source_id": f"Semantic Scholar / DOI:{doi}" if doi else "Semantic Scholar",
        })

    filtered = _filter_and_rank(raw, query)
    if not filtered:
        return "Semantic Scholar: No sufficiently relevant results found for this query."

    blocks = [
        _format_result(
            i + 1,
            r["title"], r["authors"], r["year"],
            r["source_id"], r["abstract"], r["url"], r["pdf_url"],
        )
        for i, r in enumerate(filtered)
    ]
    return f"Semantic Scholar Results ({len(filtered)} relevant):\n\n" + "\n\n".join(blocks)


# ── OpenAlex ──────────────────────────────────────────────────────────────────

def _reconstruct_abstract(inverted_index: dict) -> str:
    """Rebuild a plain-text abstract from OpenAlex's inverted index format."""
    if not inverted_index:
        return ""
    try:
        max_pos = max(pos for positions in inverted_index.values() for pos in positions)
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(w for w in words if w)
    except Exception:
        return ""


@tool(description=(
    "Search OpenAlex — the largest open scholarly database — for academic works across "
    "education, social science, cognitive science, and learning research. "
    "Strong coverage of international and open-access literature. "
    "Returns structured results with abstracts and open-access PDF links where available. "
    "Use for: broad evidence sweeps, international studies, and finding open-access full texts."
))
async def openalex_search(query: str) -> str:
    """Search OpenAlex for academic works matching the query."""
    params = {
        "search": query,
        "per-page": 15,
        "select": (
            "title,authorships,publication_year,abstract_inverted_index,"
            "open_access,doi,primary_location"
        ),
        "mailto": "research@tool",  # OpenAlex polite pool
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS) as client:
            resp = await client.get("https://api.openalex.org/works", params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return f"OpenAlex search error: {e}"

    works = data.get("results") or []
    if not works:
        return "OpenAlex: No results found."

    raw = []
    for w in works:
        doi = w.get("doi", "") or ""
        url = doi if doi.startswith("http") else (f"https://doi.org/{doi}" if doi else "")
        oa = w.get("open_access") or {}
        pdf_url = oa.get("oa_url", "") or ""
        abstract = _reconstruct_abstract(w.get("abstract_inverted_index") or {})
        ships = w.get("authorships") or []
        author_names = [
            (s.get("author") or {}).get("display_name", "")
            for s in ships[:3]
        ]
        authors_str = ", ".join(a for a in author_names if a)
        if len(ships) > 3:
            authors_str += " et al."
        raw.append({
            "title": w.get("title", "") or "",
            "abstract": abstract,
            "authors": authors_str,
            "year": str(w.get("publication_year", "") or ""),
            "url": url,
            "pdf_url": pdf_url,
            "source_id": f"OpenAlex / DOI:{doi}" if doi else "OpenAlex",
        })

    filtered = _filter_and_rank(raw, query)
    if not filtered:
        return "OpenAlex: No sufficiently relevant results found for this query."

    blocks = [
        _format_result(
            i + 1,
            r["title"], r["authors"], r["year"],
            r["source_id"], r["abstract"], r["url"], r["pdf_url"],
        )
        for i, r in enumerate(filtered)
    ]
    return f"OpenAlex Results ({len(filtered)} relevant):\n\n" + "\n\n".join(blocks)

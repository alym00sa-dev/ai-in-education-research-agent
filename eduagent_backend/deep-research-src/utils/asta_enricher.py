"""Asta paper enrichment — extract IDs from web/Tavily output and fetch full metadata."""

import asyncio
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Regex patterns for extractable paper IDs in free text
_DOI_RE = re.compile(r'\b(10\.\d{4,9}/[^\s\]\)\"\'<>,?]+)', re.IGNORECASE)
_ARXIV_RE = re.compile(r'arxiv[.:\s/]+(\d{4}\.\d{4,5}(?:v\d+)?)', re.IGNORECASE)
_PMID_RE = re.compile(r'pmid[:\s]+(\d{6,8})\b', re.IGNORECASE)
_ARXIV_URL_RE = re.compile(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)', re.IGNORECASE)
# Asta snippet_search embeds corpusId in JSON — match it directly
_CORPUS_ID_RE = re.compile(r'"corpusId"\s*:\s*"(\d+)"')

_ENRICHMENT_FIELDS = "title,abstract,authors,year,venue,publicationDate,isOpenAccess,url,tldr,citationCount"


def extract_paper_ids(text: str) -> list[str]:
    """Extract Asta-compatible paper IDs from free text (web/Tavily output)."""
    ids: list[str] = []
    seen: set[str] = set()

    def _add(pid: str):
        if pid not in seen:
            seen.add(pid)
            ids.append(pid)

    for m in _DOI_RE.finditer(text):
        _add(f"DOI:{m.group(1).rstrip('.')}")

    for m in _ARXIV_URL_RE.finditer(text):
        _add(f"ARXIV:{m.group(1)}")

    for m in _ARXIV_RE.finditer(text):
        _add(f"ARXIV:{m.group(1)}")

    for m in _PMID_RE.finditer(text):
        _add(f"PMID:{m.group(1)}")

    # Asta snippet_search JSON — corpusId is a Semantic Scholar numerical ID
    for m in _CORPUS_ID_RE.finditer(text):
        _add(f"CorpusId:{m.group(1)}")

    return ids


def _format_paper(paper: dict) -> Optional[str]:
    """Format a paper object returned by get_paper into a readable string."""
    if not paper or not isinstance(paper, dict):
        return None

    title = paper.get("title") or "Unknown title"
    year = paper.get("year", "")
    venue = paper.get("venue", "")
    url = paper.get("url", "")
    citation_count = paper.get("citationCount", "")

    authors_raw = paper.get("authors", [])
    if isinstance(authors_raw, list):
        authors = ", ".join(
            a.get("name", "") for a in authors_raw[:4] if isinstance(a, dict)
        )
        if len(authors_raw) > 4:
            authors += " et al."
    else:
        authors = str(authors_raw)

    abstract = paper.get("abstract") or ""
    tldr = (paper.get("tldr") or {})
    tldr_text = tldr.get("text", "") if isinstance(tldr, dict) else ""

    lines = [f"Title: {title}"]
    if authors:
        lines.append(f"Authors: {authors}")
    if year:
        lines.append(f"Year: {year}")
    if venue:
        lines.append(f"Venue: {venue}")
    if citation_count != "":
        lines.append(f"Citations: {citation_count}")
    if url:
        lines.append(f"URL: {url}")
    if tldr_text:
        lines.append(f"TL;DR: {tldr_text}")
    elif abstract:
        lines.append(f"Abstract: {abstract[:500]}{'...' if len(abstract) > 500 else ''}")

    return "\n".join(lines)


async def enrich_from_web_output(
    tool_output: str,
    tools_by_name: dict,
    max_papers: int = 8,
) -> str:
    """
    Extract paper IDs from web/Tavily output, fetch metadata via Asta get_paper,
    and return an enrichment block to append to the original output.

    Returns empty string if Asta is unavailable or no IDs are found.
    """
    get_paper_tool = tools_by_name.get("get_paper")
    if get_paper_tool is None:
        return ""

    ids = extract_paper_ids(tool_output)
    if not ids:
        return ""

    ids = ids[:max_papers]
    logger.info(f"[asta_enricher] Fetching {len(ids)} papers: {ids}")

    async def _fetch(paper_id: str):
        try:
            result = await asyncio.wait_for(
                get_paper_tool.ainvoke({
                    "paper_id": paper_id,
                    "fields": _ENRICHMENT_FIELDS,
                }),
                timeout=15,
            )
            return result
        except asyncio.TimeoutError:
            logger.debug(f"[asta_enricher] get_paper({paper_id}) timed out — skipping")
            return None
        except Exception as e:
            logger.debug(f"[asta_enricher] get_paper({paper_id}) failed: {e}")
            return None

    results = await asyncio.gather(*[_fetch(pid) for pid in ids])

    formatted = []
    import json
    for paper in results:
        if paper is None:
            continue
        # get_paper returns list[{'type': 'text', 'text': '<json>'}] from MCP
        if isinstance(paper, list):
            text_parts = [
                block.get("text", "") for block in paper
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            raw = "".join(text_parts)
        elif isinstance(paper, str):
            raw = paper
        elif isinstance(paper, dict):
            entry = _format_paper(paper)
            if entry:
                formatted.append(entry)
            continue
        else:
            continue
        try:
            paper = json.loads(raw)
        except Exception:
            continue
        entry = _format_paper(paper)
        if entry:
            formatted.append(entry)

    if not formatted:
        return ""

    block = "\n\n--- Asta Paper Enrichment ---\n"
    block += f"Retrieved full metadata for {len(formatted)} papers found in web results:\n\n"
    block += "\n\n".join(f"[Paper {i+1}]\n{p}" for i, p in enumerate(formatted))
    return block

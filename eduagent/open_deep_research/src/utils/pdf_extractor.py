"""PDF extraction utility — fetches full text for academic papers and produces KG-aligned PaperProfiles.

For each paper block in a tool output:
1. Extracts the PDF: and URL: fields
2. Attempts to fetch and extract full text (PyMuPDF)
   - Fast-fails on paywall (401/403), non-PDF content-type, or unreadable content
   - Derives direct PDF URL for arXiv abstract pages automatically
3. Sends text (or abstract snippet as fallback) to Haiku for structured extraction
4. Returns a PaperProfile per paper + an annotated tool output string

All papers produce a PaperProfile — extraction_status indicates full_text vs abstract_only.
The KG write step filters to full_text profiles only.
"""

import asyncio
import os
import re
from io import BytesIO

import fitz  # pymupdf
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from prompts import pdf_extraction_prompt
from state import PaperProfile

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EduResearchBot/1.0)"}

# Academic DB tools whose output this extractor runs on
PDF_EXTRACTABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
    "search_papers_by_relevance",
    "get_paper",
}


# ── URL helpers ───────────────────────────────────────────────────────────────

def _derive_pdf_url(url: str) -> str:
    """Rewrite known abstract-page URLs to their direct PDF equivalent."""
    if "arxiv.org/abs/" in url:
        pdf = url.replace("/abs/", "/pdf/")
        return pdf if pdf.endswith(".pdf") else pdf + ".pdf"
    if "arxiv.org/pdf/" in url and not url.endswith(".pdf"):
        return url + ".pdf"
    return url


# ── Block parsing ─────────────────────────────────────────────────────────────

def _parse_blocks_with_urls(text: str) -> list[dict]:
    """
    Parse a formatted tool output into a list of paper dicts.
    Each dict has: index, block (full block text), pdf_url, abstract_url.
    """
    matches = list(re.finditer(r"\[(\d+)\] Title:", text))
    results = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        pdf_url = None
        abstract_url = ""

        pdf_match = re.search(r"^\s+PDF:\s*(https?://\S+)", block, re.MULTILINE)
        if pdf_match:
            pdf_url = pdf_match.group(1).rstrip(".,);>\"'")

        url_match = re.search(r"^\s+URL:\s*(https?://\S+)", block, re.MULTILINE)
        if url_match:
            abstract_url = url_match.group(1).rstrip(".,);>\"'")

        results.append({
            "index": int(match.group(1)),
            "block": block,
            "pdf_url": pdf_url,
            "abstract_url": abstract_url,
        })
    return results


# ── Fetch + extract ───────────────────────────────────────────────────────────

async def _fetch_pdf_bytes(url: str) -> tuple[bytes | None, str]:
    """
    Fetch raw PDF bytes from a URL.
    Returns (bytes, "ok") on success or (None, reason) on fast-fail.
    """
    pdf_url = _derive_pdf_url(url)
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0, headers=_HEADERS
        ) as client:
            response = await client.get(pdf_url)

        if response.status_code in (401, 403):
            return None, f"paywall (HTTP {response.status_code})"
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"

        content_type = response.headers.get("content-type", "").lower()
        body = response.content
        is_pdf = "pdf" in content_type or "octet-stream" in content_type or body[:4] == b"%PDF"
        if not is_pdf:
            return None, "not a PDF (HTML or non-PDF content-type)"

        return body, "ok"

    except httpx.TimeoutException:
        return None, "timeout"
    except Exception as e:
        return None, f"fetch error: {type(e).__name__}"


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using PyMuPDF. Caps at 40 pages."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = min(40, len(doc))
        return "\n".join(doc[i].get_text() for i in range(pages))
    except Exception:
        return ""


# ── Haiku extraction ──────────────────────────────────────────────────────────

async def _haiku_extract(text: str, research_topic: str) -> PaperProfile:
    """Send paper text to Haiku and get back a structured PaperProfile."""
    model = init_chat_model(
        model="anthropic:claude-haiku-4-5-20251001",
        max_tokens=8192,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperProfile)

    prompt = pdf_extraction_prompt.format(
        research_topic=research_topic,
        pdf_text=text[:60000],  # ~15k tokens — full paper coverage
    )
    return await model.ainvoke([HumanMessage(content=prompt)])


# ── Per-paper extraction ──────────────────────────────────────────────────────

async def extract_paper_profile(
    paper_block: str,
    pdf_url: str | None,
    abstract_url: str,
    research_topic: str,
    source_db: str,
) -> PaperProfile:
    """
    Attempt full-text extraction for one paper.
    Falls back to the abstract snippet in the tool output block if PDF is unavailable.
    Always returns a PaperProfile — check extraction_status for full_text vs abstract_only.
    """
    text_for_extraction: str | None = None
    extraction_status = "abstract_only"
    extraction_note = ""

    # 1. Try the explicit PDF: field first
    if pdf_url:
        pdf_bytes, status = await _fetch_pdf_bytes(pdf_url)
        if pdf_bytes:
            pdf_text = _extract_text_from_pdf(pdf_bytes)
            if len(pdf_text.strip()) >= 300:
                text_for_extraction = pdf_text
                extraction_status = "full_text"
            else:
                extraction_note = "PDF too short to extract"
        else:
            extraction_note = status

    # 2. If no PDF: field, try deriving a PDF URL from the abstract URL (e.g. arXiv)
    if text_for_extraction is None and abstract_url:
        derived = _derive_pdf_url(abstract_url)
        if derived != abstract_url:  # derivation happened — worth trying
            pdf_bytes, status = await _fetch_pdf_bytes(abstract_url)
            if pdf_bytes:
                pdf_text = _extract_text_from_pdf(pdf_bytes)
                if len(pdf_text.strip()) >= 300:
                    text_for_extraction = pdf_text
                    extraction_status = "full_text"
                else:
                    extraction_note = "derived PDF too short to extract"
            else:
                extraction_note = status

    # 3. Fall back to the block text (title + abstract snippet from tool output)
    if text_for_extraction is None:
        text_for_extraction = paper_block
        if not extraction_note:
            extraction_note = "no PDF available"

    # Run Haiku structured extraction
    try:
        profile = await _haiku_extract(text_for_extraction, research_topic)
        # Override fields we know from the pipeline (more reliable than LLM extraction)
        profile.extraction_status = extraction_status
        profile.extraction_note = extraction_note
        profile.source_db = source_db
        if abstract_url and not profile.url:
            profile.url = abstract_url
        return profile

    except Exception as e:
        # Minimal fallback — extract title from block header at minimum
        title_match = re.search(r"\[\d+\] Title:\s*(.+)", paper_block)
        title = title_match.group(1).strip() if title_match else "Unknown"
        return PaperProfile(
            title=title,
            url=abstract_url,
            source_db=source_db,
            extraction_status="abstract_only",
            extraction_note=f"extraction failed: {type(e).__name__}",
        )


# ── Tool output enrichment ────────────────────────────────────────────────────

async def enrich_tool_output(
    tool_name: str,
    tool_output: str,
    research_topic: str,
) -> tuple[str, list[PaperProfile]]:
    """
    Extract PaperProfiles for every paper in a tool output string.
    Runs extractions in parallel. Injects a status annotation into each paper block.

    Returns:
        enriched_output: tool output with [FULL TEXT EXTRACTED] or [ABSTRACT ONLY — reason] per paper
        paper_profiles: list of PaperProfile objects (all papers, full_text and abstract_only)
    """
    blocks = _parse_blocks_with_urls(tool_output)
    if not blocks:
        return tool_output, []

    tasks = [
        extract_paper_profile(
            b["block"],
            b["pdf_url"],
            b["abstract_url"],
            research_topic,
            tool_name,
        )
        for b in blocks
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched = tool_output
    profiles: list[PaperProfile] = []

    for block_info, result in zip(blocks, results):
        if isinstance(result, Exception):
            tag = "[ABSTRACT ONLY — unexpected error]"
        elif result.extraction_status == "full_text":
            tag = "[FULL TEXT EXTRACTED]"
            profiles.append(result)  # only store profiles where we have real PDF text
        else:
            note = result.extraction_note or "no PDF available"
            tag = f"[ABSTRACT ONLY — {note}]"
            # abstract_only profiles are NOT stored — no value adding abstract snippets to Neo4j

        # Inject status tag at the end of the paper block
        enriched = enriched.replace(block_info["block"], block_info["block"] + f"\n  {tag}", 1)

    return enriched, profiles

"""PDF extraction — fetches full text for academic papers and produces KG-aligned PaperProfiles.

Only papers with successful full-text extraction produce a PaperProfile.
Abstract-only results are annotated but not stored.
"""

import asyncio
import os
import re
from io import BytesIO

import fitz  # pymupdf
import httpx
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from state import PaperProfile

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EduResearchBot/2.0)"}
_DEFAULT_MODEL = "gpt-5.4-mini-2026-03-17"

PDF_EXTRACTABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
}

pdf_extraction_prompt = """You are extracting structured information from an academic paper for a knowledge graph about AI in education research. Be precise. Use "not_reported" for any field where the information is genuinely absent.

Research sub-question this paper was retrieved for: {research_topic}

Paper text:
{pdf_text}

---

## Instructions

### Metadata
Extract title, DOI, year, venue (journal or conference name), population studied (e.g. "Elementary (PreK-5th)", "High School", "Undergraduate", "Adult"), user type (Student / Educator / Administrator / Parent / School / Community), and study design.

Study design must be exactly one of:
- Randomized Controlled Trial (RCT)
- Quasi-Experimental Design (QED)
- Meta-Analysis / Systematic Review
- Observational / Correlational
- Mixed-Methods
- Qualitative

### Extended Summary
Write 2-4 paragraphs covering: (1) what problem or question the paper addresses, (2) the intervention or approach studied, (3) the population and context, (4) the main conclusions. Detailed enough that a reader understands the paper without reading it.

### Outcome Assignments
Review the paper against these 9 outcome categories:
1. Academic — Literacy (reading, writing)
2. Academic — Language Fluency (speaking, listening)
3. Academic — Mathematical Numeracy
4. Academic — Scientific Reasoning
5. Academic — Other (history, arts, vocational, etc.)
6. Social-Emotional Skills (motivation, engagement, self-regulation, persistence)
7. Durable Skills (critical thinking, metacognition, collaboration, time management)
8. Operational Efficiency (productivity, task efficiency, teacher workload)
9. Systemic / Institutional Impact (policy, governance, institutional outcomes)

For each outcome the paper substantively studies (not just mentions):
- Assign a confidence score (0.0-1.0): how directly and centrally does this paper study this outcome?
- Only return outcome assignments with confidence >= 0.5
- For each included outcome, extract the empirical finding with direction, finding_summary, measure, study_size, effect_size, confidence_interval, std_deviation

### Evidence Quality and Impact Tiers (K-12 Evidence Framework)
Assign quality_tier and impact_tier — use exactly one of: blue, green, yellow, red.

Quality tier:
- blue: Meta-analysis OR well-designed RCT with all credibility and relevance criteria met
- green: Well-designed QED or meta-analysis/RCT with some concerns; 2 of 3 credibility criteria
- yellow: Correlational or qualitative study; 1 of 3 credibility criteria
- red: No clear methodology, no peer review, purely opinion/grey literature

Impact tier:
- blue: Medium or large impact on general or priority populations (effect size >= 0.20)
- green: Modest impact on priority populations or on general population (0.05-0.20)
- yellow: Modest or unclear impact on general population
- red: No impact or negative impact
"""


def _derive_pdf_url(url: str) -> str:
    if "arxiv.org/abs/" in url:
        pdf = url.replace("/abs/", "/pdf/")
        return pdf if pdf.endswith(".pdf") else pdf + ".pdf"
    if "arxiv.org/pdf/" in url and not url.endswith(".pdf"):
        return url + ".pdf"
    return url


def _parse_blocks_with_urls(text: str) -> list[dict]:
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


async def _fetch_pdf_bytes(url: str) -> tuple[bytes | None, str]:
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
            return None, "not a PDF"

        return body, "ok"
    except httpx.TimeoutException:
        return None, "timeout"
    except Exception as e:
        return None, f"fetch error: {type(e).__name__}"


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = min(40, len(doc))
        return "\n".join(doc[i].get_text() for i in range(pages))
    except Exception:
        return ""


async def _extract_profile(text: str, research_topic: str, model_name: str) -> PaperProfile:
    """Send paper text to the configured model and get back a structured PaperProfile."""
    model = init_chat_model(
        model=model_name,
        max_tokens=8192,
        api_key=os.getenv("OPENAI_API_KEY"),
        tags=["langsmith:nostream"],
    ).with_structured_output(PaperProfile)

    prompt = pdf_extraction_prompt.format(
        research_topic=research_topic,
        pdf_text=text[:60000],
    )
    return await model.ainvoke([HumanMessage(content=prompt)])


async def extract_paper_profile(
    paper_block: str,
    pdf_url: str | None,
    abstract_url: str,
    research_topic: str,
    source_db: str,
    model_name: str = _DEFAULT_MODEL,
) -> PaperProfile:
    """Attempt full-text extraction for one paper. Returns PaperProfile with extraction_status."""
    text_for_extraction: str | None = None
    extraction_status = "abstract_only"
    extraction_note = ""

    # 1. Try explicit PDF: field
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

    # 2. Try deriving PDF URL from abstract URL (e.g. arXiv)
    if text_for_extraction is None and abstract_url:
        derived = _derive_pdf_url(abstract_url)
        if derived != abstract_url:
            pdf_bytes, status = await _fetch_pdf_bytes(derived)
            if pdf_bytes:
                pdf_text = _extract_text_from_pdf(pdf_bytes)
                if len(pdf_text.strip()) >= 300:
                    text_for_extraction = pdf_text
                    extraction_status = "full_text"
                else:
                    extraction_note = "derived PDF too short"
            else:
                extraction_note = status

    # 3. Fall back to abstract snippet from block text
    if text_for_extraction is None:
        text_for_extraction = paper_block
        if not extraction_note:
            extraction_note = "no PDF available"

    try:
        profile = await _extract_profile(text_for_extraction, research_topic, model_name)
        profile.extraction_status = extraction_status
        profile.extraction_note = extraction_note
        profile.source_db = source_db
        if abstract_url and not profile.url:
            profile.url = abstract_url
        return profile
    except Exception as e:
        title_match = re.search(r"\[\d+\] Title:\s*(.+)", paper_block)
        title = title_match.group(1).strip() if title_match else "Unknown"
        return PaperProfile(
            title=title,
            url=abstract_url,
            source_db=source_db,
            extraction_status="abstract_only",
            extraction_note=f"extraction failed: {type(e).__name__}",
        )


async def enrich_tool_output(
    tool_name: str,
    tool_output: str,
    research_topic: str,
    model_name: str = _DEFAULT_MODEL,
) -> tuple[str, list[PaperProfile]]:
    """Extract PaperProfiles for all papers in a tool output string.

    Only full_text profiles are returned — abstract-only profiles are NOT stored.

    Returns:
        enriched_output: annotated string with [FULL TEXT EXTRACTED] or [ABSTRACT ONLY — reason]
        paper_profiles: list of full-text PaperProfile objects only
    """
    blocks = _parse_blocks_with_urls(tool_output)
    if not blocks:
        return tool_output, []

    tasks = [
        extract_paper_profile(
            b["block"], b["pdf_url"], b["abstract_url"],
            research_topic, tool_name, model_name,
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
            profiles.append(result)
        else:
            note = result.extraction_note or "no PDF available"
            tag = f"[ABSTRACT ONLY — {note}]"

        enriched = enriched.replace(
            block_info["block"],
            block_info["block"] + f"\n  {tag}",
            1,
        )

    return enriched, profiles

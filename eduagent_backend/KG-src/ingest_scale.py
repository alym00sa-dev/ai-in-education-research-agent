"""SCALE Stanford AI Repository scraper + ingestion pipeline.

Scrapes https://scale.stanford.edu/ai/repository (1,155 curated papers),
pre-filters to empirical/review study designs, applies our LLM relevance
filter, then runs pdf_extractor_v2 with the direct arXiv PDF URL.

Usage:
    python citation-kg-testing/ingest_scale.py
    python citation-kg-testing/ingest_scale.py --max-detail-concurrency 10 --dry-run
"""

import asyncio
import json
import os
import re
import sys
import argparse
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

_SCRIPT_DIR  = Path(__file__).resolve().parent
BACKEND_ROOT = _SCRIPT_DIR.parent  # KG-src lives inside eduagent_backend
load_dotenv(BACKEND_ROOT / ".env")
sys.path.insert(0, str(BACKEND_ROOT / "deep-research-src"))

import httpx
from bs4 import BeautifulSoup
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from utils.pdf_extractor_kg import (
    extract_paper_profile_v2,
    PaperProfileV2,
)

# ── Config ────────────────────────────────────────────────────────────────────

SCALE_BASE          = "https://scale.stanford.edu/ai/repository"
TOTAL_PAGES         = 39
RESEARCH_TOPIC      = "AI tools and interventions in education: effectiveness, student outcomes, and learning"
RELEVANCE_THRESHOLD = 5     # out of 7
MIN_YEAR            = 2026

FILTER_MODEL     = "gpt-5.5-2026-04-23"
EXTRACTION_MODEL = "gpt-5.5-2026-04-23"

# NEW_PAPER_MARKER removed — we scrape page 1 only (most recent) and rely on
# MIN_YEAR + Neo4j dedup to skip already-ingested papers.

# Study design tags from SCALE that indicate empirical / review work.
# Papers tagged with ANY of these pass the pre-filter.
EMPIRICAL_DESIGN_TAGS = {
    "impact – randomized controlled trial",
    "impact – quasi-experimental",   # hyphen variant
    "impact – quasi–experimental",   # en-dash variant (site inconsistency)
    "systematic review",
    "quantitative – others",
    "quantitative – survey",
}

_DEFAULT_OUTPUT = BACKEND_ROOT / "KG-src" / "ingested_papers" / str(date.today()) / "scale"
OUTPUT_DIR = _DEFAULT_OUTPUT  # overridden by --output-dir at parse time

HTTP_TIMEOUT = 20.0
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-scraper/1.0)"}


# ── Step 1: Scrape listing pages ──────────────────────────────────────────────

async def _fetch_listing_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    """Return [{title, slug, study_design_tags}] for one listing page."""
    url = SCALE_BASE if page == 1 else f"{SCALE_BASE}?page={page}"
    try:
        resp = await client.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ✗ listing page {page} failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    papers = []
    for card in soup.select("li.col div.card"):
        link = card.select_one("h5 a")
        if not link:
            continue
        title = link.get_text(strip=True)
        href  = link.get("href", "")
        slug  = href.rstrip("/").split("/")[-1]

        # Extract study design tags from the card directly
        study_design_tags = []
        for strong in card.find_all("strong"):
            if "Study design" in strong.get_text():
                # Sibling <a> tags are the design tags
                parent = strong.parent
                for a in parent.find_all("a"):
                    tag = a.get_text(strip=True).lower()
                    study_design_tags.append(tag)
                break

        papers.append({"title": title, "slug": slug, "study_design_tags": study_design_tags})
    return papers


async def _fetch_listing_page_sem(
    client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore
) -> list[dict]:
    async with sem:
        return await _fetch_listing_page(client, page)


async def scrape_all_listings(max_pages: int, concurrency: int = 4) -> list[dict]:
    """Scrape listing pages with controlled concurrency. Returns [{title, slug}]."""
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True) as client:
        tasks = [_fetch_listing_page_sem(client, p, sem) for p in range(1, max_pages + 1)]
        results = await asyncio.gather(*tasks)
    papers = [item for batch in results for item in batch]
    print(f"  {len(papers)} papers found across {max_pages} listing pages")
    return papers


# ── Step 2: Fetch detail pages ────────────────────────────────────────────────

async def _fetch_detail(
    client: httpx.AsyncClient, entry: dict, sem: asyncio.Semaphore
) -> dict:
    """Fetch arXiv link and abstract from a paper's detail page."""
    url = f"{SCALE_BASE}/{entry['slug']}"
    async with sem:
        try:
            resp = await client.get(url, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
        except Exception as e:
            return {**entry, "arxiv_id": None, "pdf_url": None,
                    "abstract_url": None, "abstract": "", "detail_error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")

    # arXiv link — may be /abs/ or /pdf/
    arxiv_id = pdf_url = abstract_url = None
    for a in soup.find_all("a", href=True):
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([\d.]+)", a["href"])
        if m:
            arxiv_id     = m.group(1)
            abstract_url = f"https://arxiv.org/abs/{arxiv_id}"
            pdf_url      = f"https://arxiv.org/pdf/{arxiv_id}"
            break

    # Abstract
    abstract = ""
    for sel in [".field--name-body", ".field-name-body", ".field--name-field-abstract"]:
        node = soup.select_one(sel)
        if node:
            abstract = node.get_text(" ", strip=True)[:1500]
            break

    return {**entry, "arxiv_id": arxiv_id, "pdf_url": pdf_url,
            "abstract_url": abstract_url, "abstract": abstract}


async def fetch_all_details(
    papers: list[dict], max_concurrency: int
) -> list[dict]:
    """Fetch detail pages for all papers, respecting concurrency limit."""
    sem = asyncio.Semaphore(max_concurrency)
    async with httpx.AsyncClient(headers=HTTP_HEADERS, follow_redirects=True) as client:
        tasks = [_fetch_detail(client, p, sem) for p in papers]
        enriched = await asyncio.gather(*tasks)
    return list(enriched)


# ── Step 3: Pre-filter by study design ────────────────────────────────────────

def prefilter_empirical(papers: list[dict]) -> list[dict]:
    """Keep only papers tagged with empirical / review study designs AND with an arXiv link."""
    kept = [p for p in papers if any(
        tag in EMPIRICAL_DESIGN_TAGS for tag in p.get("study_design_tags", [])
    )]
    with_pdf = [p for p in kept if p.get("pdf_url")]
    print(f"  {len(kept)}/{len(papers)} passed design filter")
    print(f"  {len(kept) - len(with_pdf)} dropped (no arXiv link found)")
    return with_pdf


# ── Step 4: LLM relevance filter ─────────────────────────────────────────────

_SCORE_PROMPT = """You are scoring academic papers for relevance to a research topic.

Research topic: {research_topic}

Papers:
{papers_text}

Score every paper [N] on a 0-7 scale:
0 = completely irrelevant
1 = very tangential (different field)
2 = tangentially related (same domain, wrong intervention)
3 = indirect evidence (right domain, different population or design)
4 = somewhat relevant — addresses the topic with gaps
5 = relevant — addresses the topic with some empirical evidence
6 = directly relevant — strong match on topic, population, and design
7 = direct hit — precisely addresses the topic with rigorous evidence

Return a score for every paper listed."""


class _PaperScore(BaseModel):
    index: int
    score: int = Field(ge=0, le=7)


class _ScoreResult(BaseModel):
    papers: list[_PaperScore]


def _build_block(paper: dict, index: int) -> str:
    """Build a text block for the relevance scorer from SCALE paper data."""
    return (
        f"[{index}] Title: {paper['title']}\n"
        f"Study design tags: {', '.join(paper.get('study_design_tags', []))}\n"
        f"Abstract: {paper.get('abstract', '')[:600]}"
    )


async def _score_batch(blocks_text: str) -> dict[int, int]:
    try:
        model = init_chat_model(
            model=FILTER_MODEL,
            max_tokens=2048,
            api_key=os.getenv("OPENAI_API_KEY", ""),
            tags=["langsmith:nostream"],
        ).with_structured_output(_ScoreResult)
        result: _ScoreResult = await model.ainvoke([
            HumanMessage(content=_SCORE_PROMPT.format(
                research_topic=RESEARCH_TOPIC,
                papers_text=blocks_text[:10000],
            ))
        ])
        return {p.index: p.score for p in result.papers}
    except Exception as e:
        print(f"    ⚠ Scoring failed: {e} — passing all through at score=3")
        return {}


async def relevance_filter(papers: list[dict]) -> list[dict]:
    """Score all papers in batches of 20, keep those ≥ RELEVANCE_THRESHOLD."""
    BATCH = 20
    passing = []
    for batch_start in range(0, len(papers), BATCH):
        batch = papers[batch_start: batch_start + BATCH]
        blocks = [_build_block(p, i) for i, p in enumerate(batch)]
        scores = await _score_batch("\n\n".join(blocks))
        for i, p in enumerate(batch):
            score = scores.get(i, 3)
            if score >= RELEVANCE_THRESHOLD:
                passing.append({**p, "relevance_score": score})
    print(f"  {len(passing)}/{len(papers)} passed relevance filter (≥{RELEVANCE_THRESHOLD}/7)")
    return passing


# ── Output helpers ────────────────────────────────────────────────────────────

def _doi_slug(doi: str | None, title: str) -> str:
    if doi:
        return re.sub(r"[^a-z0-9]+", "_", doi.lower())[:60]
    return re.sub(r"[^a-z0-9]+", "_", title.lower())[:50]


def _write_profile(profile: PaperProfileV2, output_dir: Path) -> str:
    slug = _doi_slug(profile.doi, profile.title)
    path = output_dir / f"{slug}.json"
    path.write_text(json.dumps(profile.model_dump(), indent=2))
    return f"{slug}.json"


def _write_summary(profiles: list[PaperProfileV2], files: list[str], output_dir: Path):
    summary = [
        {
            "doi":            profile.doi,
            "title":          profile.title,
            "year":           profile.year,
            "study_design":   profile.study_design,
            "verdict":        profile.verdict,
            "tools":          [t.name for t in profile.identified_tools],
            "quality_tier":   profile.quality_tier,
            "impact_tier":    profile.impact_tier,
            "citation_count": len(profile.citations),
            "source_db":      profile.source_db,
            "file":           fname,
        }
        for profile, fname in zip(profiles, files)
    ]
    (output_dir / "_summary.json").write_text(json.dumps(summary, indent=2))


def _build_citation_index(profiles: list[PaperProfileV2]) -> list[dict]:
    seen: dict[str, dict] = {}
    for profile in profiles:
        citing_doi = profile.doi or profile.title[:50]
        for ref in profile.citations:
            key = ref.doi.lower() if ref.doi else ref.title.lower()[:80]
            if key not in seen:
                seen[key] = {
                    "title": ref.title,
                    "doi":   ref.doi,
                    "year":  ref.year,
                    "venue": ref.venue,
                    "cited_by_count": 0,
                    "cited_by": [],
                }
            entry = seen[key]
            if citing_doi not in entry["cited_by"]:
                entry["cited_by"].append(citing_doi)
                entry["cited_by_count"] += 1
    return sorted(seen.values(), key=lambda x: -x["cited_by_count"])


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(max_pages: int, max_detail_concurrency: int, dry_run: bool):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nSCALE ingestion — pages 1–{max_pages} of {TOTAL_PAGES}")
    print(f"Output: {OUTPUT_DIR}\n")

    # ── 1. Scrape listings ────────────────────────────────────────────────────
    print("Step 1: Scraping listing pages...")
    pages_to_scrape = 1 if dry_run else max_pages
    all_papers = await scrape_all_listings(pages_to_scrape)
    if dry_run:
        print(f"  [dry-run] scraping page 1 only ({len(all_papers)} papers)\n")

    if not all_papers:
        print("No papers found on listing page — nothing to ingest.")
        return
    print(f"  {len(all_papers)} papers on page 1 (most recent)\n")

    # ── 2. Pre-filter by study design (tags already in listing) ──────────────
    print("\nStep 2: Study design pre-filter...")
    design_passed = [p for p in all_papers if any(
        tag in EMPIRICAL_DESIGN_TAGS for tag in p.get("study_design_tags", [])
    )]
    print(f"  {len(design_passed)}/{len(all_papers)} passed design filter")

    if not design_passed:
        print("No papers passed design filter — check EMPIRICAL_DESIGN_TAGS or listing parser.")
        return

    # ── 3. Fetch detail pages only for design-filtered papers ─────────────────
    print(f"\nStep 3: Fetching {len(design_passed)} detail pages (concurrency={max_detail_concurrency})...")
    enriched = await fetch_all_details(design_passed, max_detail_concurrency)
    no_arxiv = sum(1 for p in enriched if not p.get("arxiv_id"))
    print(f"  {len(enriched) - no_arxiv}/{len(enriched)} have arXiv links")
    candidates = [p for p in enriched if p.get("pdf_url")]

    if not candidates:
        print("No candidates with arXiv links after design filter.")
        return

    # ── 4. LLM relevance filter ───────────────────────────────────────────────
    print(f"\nStep 4: LLM relevance scoring ({len(candidates)} papers)...")
    relevant = await relevance_filter(candidates)

    if not relevant:
        print("No papers passed relevance filter.")
        return

    (OUTPUT_DIR / "_candidates.json").write_text(json.dumps(relevant, indent=2))
    print(f"  Saved {len(relevant)} candidates to _candidates.json")

    # ── 5. Extract ────────────────────────────────────────────────────────────
    print(f"\nStep 5: PDF extraction for {len(relevant)} papers...")
    extract_tasks = [
        extract_paper_profile_v2(
            paper_block=_build_block(p, i),
            pdf_url=p["pdf_url"],
            abstract_url=p.get("abstract_url"),
            research_topic=RESEARCH_TOPIC,
            source_db="scale_stanford",
            metadata_model=EXTRACTION_MODEL,
            taxonomy_model=EXTRACTION_MODEL,
        )
        for i, p in enumerate(relevant)
    ]
    raw_profiles = await asyncio.gather(*extract_tasks)

    profiles: list[PaperProfileV2] = []
    dropped_abstract = dropped_year = dropped_verdict = 0

    for p in raw_profiles:
        if isinstance(p, Exception):
            continue
        if p.extraction_status != "full_text":
            dropped_abstract += 1
            continue
        if p.year is not None and p.year < MIN_YEAR:
            dropped_year += 1
            continue
        if p.verdict == "no_tool":
            dropped_verdict += 1
            continue
        if p.verdict == "framework_only" and (
            p.quality_tier == "red" or p.study_design == "Qualitative"
        ):
            dropped_verdict += 1
            continue
        profiles.append(p)

    print(f"\n{len(profiles)} full-text profiles kept")
    print(f"{dropped_abstract} abstract-only / failed (dropped)")
    print(f"{dropped_year} dropped for year < {MIN_YEAR}")
    print(f"{dropped_verdict} dropped for verdict=no_tool or framework_only+red\n")

    # Final DOI dedup
    final_profiles: list[PaperProfileV2] = []
    final_dois: set[str] = set()
    for p in profiles:
        key = p.doi.lower() if p.doi else p.title.lower()[:80]
        if key not in final_dois:
            final_dois.add(key)
            final_profiles.append(p)

    print(f"{len(final_profiles)} papers after final DOI dedup\n")

    # ── 6. Write output ───────────────────────────────────────────────────────
    files = []
    for profile in final_profiles:
        fname = _write_profile(profile, OUTPUT_DIR)
        files.append(fname)
        tools = [t.name for t in profile.identified_tools]
        print(f"  ✓ {profile.title[:65]}")
        print(f"    verdict={profile.verdict} | tools={tools} | design={profile.study_design}")
        print(f"    quality={profile.quality_tier} | citations={len(profile.citations)} | file={fname}")

    _write_summary(final_profiles, files, OUTPUT_DIR)

    citation_index = _build_citation_index(final_profiles)
    (OUTPUT_DIR / "_citations.json").write_text(json.dumps(citation_index, indent=2))

    print(f"\n{'='*60}")
    print(f"Done: {len(final_profiles)} papers written to {OUTPUT_DIR}")
    print(f"      {sum(len(p.citations) for p in final_profiles)} total citations extracted")
    print(f"      {len(citation_index)} unique cited works in _citations.json")

    verdicts = {}
    for p in final_profiles:
        verdicts[p.verdict] = verdicts.get(p.verdict, 0) + 1
    print(f"\nVerdicts: {verdicts}")

    tiers = {}
    for p in final_profiles:
        tiers[p.quality_tier] = tiers.get(p.quality_tier, 0) + 1
    print(f"Quality tiers: {tiers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-pages", type=int, default=1,
                        help=f"Max listing pages to scrape (default: 1 — first page only for new papers)")
    parser.add_argument("--max-detail-concurrency", type=int, default=8,
                        help="Max concurrent detail page fetches (default: 8)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Cap to first 30 papers for testing")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Override output directory (default: KG-src/ingested_papers/scale_YYYY-MM-DD)")
    args = parser.parse_args()
    if args.output_dir:
        OUTPUT_DIR = args.output_dir
    asyncio.run(main(args.max_pages, args.max_detail_concurrency, args.dry_run))

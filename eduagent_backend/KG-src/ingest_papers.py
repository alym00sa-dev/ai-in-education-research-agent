"""Dry-run ingestion pipeline — search, filter, extract, output for manual review.

Runs 4 queries across 4 academic DBs, filters by relevance (≥ 3/7),
fetches full-text PDFs, and runs 3-call extraction (metadata + KG taxonomy + citations).

Usage:
    python citation-kg-testing/ingest_papers.py
    python citation-kg-testing/ingest_papers.py --results-per-query 5 --concurrency 3
"""

import asyncio
import json
import os
import re
import sys
import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

_SCRIPT_DIR  = Path(__file__).resolve().parent
BACKEND_ROOT = _SCRIPT_DIR.parent  # KG-src lives inside eduagent_backend
load_dotenv(BACKEND_ROOT / ".env")
sys.path.insert(0, str(BACKEND_ROOT / "deep-research-src"))

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from utils.academic_search import (
    eric_search,
    openalex_search,
    arxiv_search,
    semantic_scholar_search,
)
from utils.pdf_extractor_kg import (
    extract_paper_profile_v2,
    _parse_blocks_with_urls,
    _extract_profile_v2,
    PaperProfileV2,
)

# ── Config ────────────────────────────────────────────────────────────────────

RESEARCH_TOPIC = "AI tools and interventions in education: effectiveness, student outcomes, and learning"

QUERIES = [
    # Tool-specific
    "ChatGPT education student learning outcomes 2023",
    "large language model tutoring higher education",
    "AI writing assistant feedback academic performance",
    "intelligent tutoring system mathematics K-12 RCT",
    "adaptive learning platform personalized instruction",
    "generative AI classroom engagement outcomes",
    "conversational AI chatbot student learning",
    "AI automated feedback writing composition",
    "AI reading literacy tool elementary",
    "AI language learning second language acquisition",
    # Topic / outcome
    "artificial intelligence student self-regulated learning motivation",
    "AI formative assessment student performance",
    "machine learning early warning dropout prediction",
    "AI teacher professional development effectiveness",
    "educational technology equity access underserved AI",
    # Framework / emerging
    "AI education ethical framework policy higher education",
    "large language model pedagogy learner simulation",
    "generative AI academic integrity student trust",
    "AI curriculum design learning theory framework",
    "human-AI collaboration classroom blended learning design",
    # Named tools
    "Khanmigo Khan Academy AI tutor outcomes",
    "Duolingo AI language learning effectiveness",
    "ASSISTments intelligent tutoring math achievement",
    "MATHia Carnegie Learning adaptive math",
    "Photomath AI math problem solving students",
    # Emerging / underrepresented
    "AI STEM science reasoning outcomes intervention",
    "AI programming education coding learning",
    "multimodal AI accessibility special education",
    # GenAI × K-12 students
    "GenAI K-12 student achievement",
    "ChatGPT middle school writing",
    "LLM high school science",
    "AI elementary math fluency",
    "generative AI gifted students",
    # GenAI × higher ed students
    "ChatGPT undergraduate academic performance",
    "LLM college essay feedback",
    "AI graduate research support",
    "GenAI community college retention",
    "ChatGPT first-generation students",
    # GenAI × teachers / instructors
    "LLM teacher lesson planning",
    "AI instructor grading efficiency",
    "ChatGPT faculty professional development",
    "GenAI teacher workload reduction",
    # GenAI × special populations
    "AI ESL English language learners",
    "ChatGPT dyslexia reading support",
    "LLM autism communication intervention",
    "GenAI low-income school outcomes",
    "AI rural education access",
    # GenAI × subject domains
    "ChatGPT medical education clinical reasoning",
    "LLM law school exam preparation",
    "AI business education simulation",
    "GenAI art creativity education",
    "ChatGPT social studies critical thinking",
]

# ── Batch 2 queries (75 queries) ──────────────────────────────────────────────
# Run with: python ingest_papers.py --batch 2
# Strategy: 10 non-ChatGPT LLM family queries + 40 broad short AI/LLM/GenAI × education
#           + 25 new 3-word queries covering underrepresented populations, subjects, outcomes

QUERIES_B2 = [
    # ── Non-ChatGPT LLM families (10) ─────────────────────────────────────────
    "Claude classroom",
    "Claude writing feedback",
    "Gemini learning outcomes",
    "Gemini STEM education",
    "LLaMA tutoring",
    "LLaMA higher education",
    "DeepSeek students",
    "Mistral education",
    "Kimi AI education",
    "Qwen learning",

    # ── AI × education (20) ───────────────────────────────────────────────────
    "AI classroom",
    "AI tutoring",
    "AI reading",
    "AI writing",
    "AI math",
    "AI grading",
    "AI feedback",
    "AI engagement",
    "AI retention",
    "AI motivation",
    "AI equity",
    "AI literacy",
    "AI STEM",
    "AI special education",
    "AI primary school",
    "AI undergraduate",
    "AI medical school",
    "AI teachers",
    "AI achievement",
    "AI coding",

    # ── LLM × education (10) ──────────────────────────────────────────────────
    "LLM students",
    "LLM college",
    "LLM writing",
    "LLM math",
    "LLM ESL",
    "LLM EFL",
    "LLM comprehension",
    "LLM curriculum",
    "LLM pedagogy",
    "LLM science",

    # ── GenAI × education (10) ────────────────────────────────────────────────
    "GenAI teacher",
    "GenAI feedback",
    "GenAI assessment",
    "GenAI science",
    "GenAI K-12",
    "GenAI engagement",
    "GenAI coding",
    "GenAI nursing",
    "GenAI creativity",
    "GenAI outcomes",

    # ── New 3-word queries: populations (6) ───────────────────────────────────
    "AI graduate students",
    "GenAI low-income",
    "AI gifted students",
    "GenAI rural education",
    "GenAI early childhood",
    "GenAI international students",

    # ── New 3-word queries: subjects / domains (5) ────────────────────────────
    "LLM biology education",
    "AI history education",
    "LLM engineering education",
    "GenAI vocational training",
    "AI language learning",

    # ── New 3-word queries: outcomes / skills (8) ─────────────────────────────
    "LLM critical thinking",
    "GenAI problem solving",
    "GenAI self-efficacy",
    "AI metacognition",
    "AI academic integrity",
    "LLM collaboration",
    "AI self-regulated learning",
    "LLM academic writing",

    # ── New 3-word queries: settings / use cases (6) ──────────────────────────
    "AI blended learning",
    "LLM online learning",
    "LLM formative assessment",
    "LLM assessment design",
    "GenAI personalization",
    "AI professional development",
]

DATABASES = [
    ("eric_search",              eric_search),
    ("openalex_search",          openalex_search),
    ("arxiv_search",             arxiv_search),
    ("semantic_scholar_search",  semantic_scholar_search),
]

RELEVANCE_THRESHOLD = 3      # out of 7 (default)
ARXIV_THRESHOLD     = 2      # arXiv papers are more technical/theoretical — lower bar
MIN_YEAR            = 2026   # drop papers published before this
FILTER_MODEL        = "gpt-5.5-2026-04-23"
EXTRACTION_MODEL    = "gpt-5.5-2026-04-23"

_DEFAULT_OUTPUT = BACKEND_ROOT / "KG-src" / "ingested_papers" / str(date.today()) / "papers"
OUTPUT_DIR = _DEFAULT_OUTPUT  # overridden by --output-dir at parse time


# ── Relevance scoring ─────────────────────────────────────────────────────────

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


async def _score_blocks(blocks_text: str) -> dict[int, int]:
    """Return {block_index: score} for all blocks."""
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
                papers_text=blocks_text[:8000],
            ))
        ])
        return {p.index: p.score for p in result.papers}
    except Exception as e:
        print(f"    ⚠ Scoring failed: {e} — passing all through at score=3")
        return {}


# ── DOI / title dedup ─────────────────────────────────────────────────────────

def _extract_doi_from_block(block: str) -> str | None:
    m = re.search(r"10\.\d{4,}/\S+", block)
    return m.group(0).rstrip(".,);>\"'") if m else None


def _extract_year_from_block(block: str) -> int | None:
    """Best-effort year extraction from block text (e.g. 'Authors: Smith (2023)')."""
    m = re.search(r"\((\d{4})\)", block)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(20\d{2})\b", block)
    return int(m.group(1)) if m else None


def _title_key(block: str) -> str:
    m = re.search(r"\[\d+\] Title:\s*(.+)", block)
    if not m:
        return block[:60].lower()
    return re.sub(r"\s+", " ", m.group(1).strip().lower())[:80]


# ── Search + filter ───────────────────────────────────────────────────────────

async def search_and_filter(
    query: str,
    db_name: str,
    db_fn,
    results_per_query: int,
    sem: asyncio.Semaphore,
) -> list[dict]:
    """Run one query against one DB, score, return passing blocks with metadata."""
    async with sem:
        try:
            raw: str = await db_fn.ainvoke(query)
        except Exception as e:
            print(f"    ✗ {db_name} failed: {e}")
            return []

    blocks_info = _parse_blocks_with_urls(raw)
    if not blocks_info:
        return []

    # Limit results per query
    blocks_info = blocks_info[:results_per_query]

    # Rebuild text for scoring
    blocks_text = "\n\n".join(b["block"] for b in blocks_info)
    scores = await _score_blocks(blocks_text)

    threshold = ARXIV_THRESHOLD if db_name == "arxiv_search" else RELEVANCE_THRESHOLD
    passing = []
    for b in blocks_info:
        score = scores.get(b["index"], 3)  # default 3 if not scored
        if score < threshold:
            continue
        # Pre-filter by year if detectable from block text
        year_hint = _extract_year_from_block(b["block"])
        if year_hint and year_hint < MIN_YEAR:
            continue
        passing.append({
            **b,
            "relevance_score": score,
            "source_db": db_name,
            "query": query,
            "doi_hint": _extract_doi_from_block(b["block"]),
            "title_key": _title_key(b["block"]),
        })

    print(f"    {db_name}: {len(passing)}/{len(blocks_info)} passed (threshold ≥{threshold}, year ≥{MIN_YEAR})")
    return passing


# ── Query performance tracking ────────────────────────────────────────────────

def _build_query_stats(
    candidates: list[dict],
    final_profiles_by_query: dict[str, int],
) -> list[dict]:
    """Aggregate per-query stats: candidates, full-text papers, DBs that contributed."""
    from collections import defaultdict
    stats: dict[str, dict] = defaultdict(lambda: {
        "candidates": 0,
        "full_text": 0,
        "dbs": set(),
    })
    for c in candidates:
        q = c["query"]
        stats[q]["candidates"] += 1
        stats[q]["dbs"].add(c["source_db"])
    for q, count in final_profiles_by_query.items():
        stats[q]["full_text"] += count
    result = []
    for q, s in stats.items():
        result.append({
            "query": q,
            "candidates": s["candidates"],
            "full_text": s["full_text"],
            "dbs": sorted(s["dbs"]),
        })
    return sorted(result, key=lambda x: (-x["full_text"], -x["candidates"]))


# ── Citation aggregation ──────────────────────────────────────────────────────

def _build_citation_index(profiles: list[PaperProfileV2]) -> list[dict]:
    """Flatten all citations, dedup by DOI/title, count how many papers cite each."""
    seen: dict[str, dict] = {}  # key → entry

    for profile in profiles:
        citing_doi = profile.doi or profile.title[:50]
        for ref in profile.citations:
            key = ref.doi.lower() if ref.doi else ref.title.lower()[:80]
            if key not in seen:
                seen[key] = {
                    "title": ref.title,
                    "doi": ref.doi,
                    "year": ref.year,
                    "venue": ref.venue,
                    "cited_by_count": 0,
                    "cited_by": [],
                }
            entry = seen[key]
            if citing_doi not in entry["cited_by"]:
                entry["cited_by"].append(citing_doi)
                entry["cited_by_count"] += 1

    return sorted(seen.values(), key=lambda x: -x["cited_by_count"])


# ── Output helpers ────────────────────────────────────────────────────────────

def _doi_slug(doi: str | None, title: str) -> str:
    if doi:
        return re.sub(r"[^a-z0-9]+", "_", doi.lower())[:60]
    return re.sub(r"[^a-z0-9]+", "_", title.lower())[:50]


def _write_profile(profile: PaperProfileV2, output_dir: Path) -> str:
    slug = _doi_slug(profile.doi, profile.title)
    path = output_dir / f"{slug}.json"
    data = profile.model_dump()
    path.write_text(json.dumps(data, indent=2))
    return f"{slug}.json"


def _write_summary(profiles: list[PaperProfileV2], files: list[str], output_dir: Path):
    summary = []
    for profile, fname in zip(profiles, files):
        summary.append({
            "doi": profile.doi,
            "title": profile.title,
            "year": profile.year,
            "study_design": profile.study_design,
            "verdict": profile.verdict,
            "tools": [t.name for t in profile.identified_tools],
            "quality_tier": profile.quality_tier,
            "impact_tier": profile.impact_tier,
            "citation_count": len(profile.citations),
            "source_db": profile.source_db,
            "file": fname,
        })
    (output_dir / "_summary.json").write_text(json.dumps(summary, indent=2))


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(results_per_query: int, concurrency: int, max_queries: int | None = None, batch: int = 1):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    query_pool = QUERIES if batch == 1 else QUERIES_B2
    queries = query_pool[:max_queries] if max_queries else query_pool
    print(f"\nIngestion — batch {batch} — {len(queries)} queries × {len(DATABASES)} DBs")
    if max_queries:
        print(f"[dry-run] capped to first {max_queries} queries")
    print(f"Results per query per DB: {results_per_query}")
    print(f"Relevance threshold: ≥{RELEVANCE_THRESHOLD}/7")
    print(f"Output: {OUTPUT_DIR}\n")

    sem = asyncio.Semaphore(concurrency)

    # ── Step 1: Search all query × DB combinations ────────────────────────────
    search_tasks = [
        search_and_filter(query, db_name, db_fn, results_per_query, sem)
        for query in queries
        for db_name, db_fn in DATABASES
    ]
    print(f"Running {len(search_tasks)} search tasks ({len(queries)} queries × {len(DATABASES)} DBs)...")
    all_results = await asyncio.gather(*search_tasks)
    candidates = [item for batch in all_results for item in batch]
    print(f"\n{len(candidates)} candidates after relevance filter\n")

    # ── Step 2: Dedup ─────────────────────────────────────────────────────────
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    unique_candidates = []

    for c in candidates:
        doi = c.get("doi_hint")
        tkey = c["title_key"]
        if doi and doi in seen_dois:
            continue
        if tkey in seen_titles:
            continue
        if doi:
            seen_dois.add(doi)
        seen_titles.add(tkey)
        unique_candidates.append(c)

    print(f"{len(unique_candidates)} unique candidates after dedup\n")

    # ── Step 3: Extract ───────────────────────────────────────────────────────
    print("Running PDF extraction (full-text only)...")
    extract_tasks = [
        extract_paper_profile_v2(
            paper_block=c["block"],
            pdf_url=c["pdf_url"],
            abstract_url=c["abstract_url"],
            research_topic=RESEARCH_TOPIC,
            source_db=c["source_db"],
            metadata_model=EXTRACTION_MODEL,
            taxonomy_model=EXTRACTION_MODEL,
        )
        for c in unique_candidates
    ]
    raw_profiles = await asyncio.gather(*extract_tasks)

    # Keep only full-text with year >= MIN_YEAR
    # Drop no_tool and framework_only+red (no educational value)
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

    # Post-extraction DOI dedup
    final_profiles: list[PaperProfileV2] = []
    final_dois: set[str] = set()
    for p in profiles:
        key = p.doi.lower() if p.doi else p.title.lower()[:80]
        if key not in final_dois:
            final_dois.add(key)
            final_profiles.append(p)

    print(f"{len(final_profiles)} papers after final DOI dedup\n")

    # Build title_key → query reverse lookup from candidates
    title_to_query: dict[str, str] = {
        c["title_key"]: c["query"] for c in unique_candidates
    }

    # ── Step 4: Write output ──────────────────────────────────────────────────
    files = []
    profiles_by_query: dict[str, int] = {}
    for profile in final_profiles:
        fname = _write_profile(profile, OUTPUT_DIR)
        files.append(fname)
        tools = [t.name for t in profile.identified_tools]
        print(f"  ✓ {profile.title[:65]}")
        print(f"    verdict={profile.verdict} | tools={tools} | design={profile.study_design}")
        print(f"    quality={profile.quality_tier} | citations={len(profile.citations)} | file={fname}")
        # Map back to originating query via title key
        tkey = re.sub(r"\s+", " ", profile.title.strip().lower())[:80]
        src_query = title_to_query.get(tkey)
        if src_query:
            profiles_by_query[src_query] = profiles_by_query.get(src_query, 0) + 1

    _write_summary(final_profiles, files, OUTPUT_DIR)

    citation_index = _build_citation_index(final_profiles)
    (OUTPUT_DIR / "_citations.json").write_text(json.dumps(citation_index, indent=2))

    # ── Query performance stats ───────────────────────────────────────────────
    query_stats = _build_query_stats(unique_candidates, profiles_by_query)
    (OUTPUT_DIR / "_query_stats.json").write_text(json.dumps(query_stats, indent=2))

    print(f"\nTop queries by full-text yield:")
    for s in query_stats[:10]:
        bar = "█" * s["full_text"] + "░" * max(0, 3 - s["full_text"])
        print(f"  {bar} {s['full_text']} ft | {s['candidates']} cand | {s['query'][:55]}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Done: {len(final_profiles)} papers written to {OUTPUT_DIR}")
    print(f"      {sum(len(p.citations) for p in final_profiles)} total citations extracted")
    print(f"      {len(citation_index)} unique cited works in _citations.json")
    print(f"      {len(query_stats)} queries tracked → _query_stats.json")

    verdicts = {}
    for p in final_profiles:
        verdicts[p.verdict] = verdicts.get(p.verdict, 0) + 1
    print(f"\nVerdicts: {verdicts}")

    tiers = {}
    for p in final_profiles:
        tiers[p.quality_tier] = tiers.get(p.quality_tier, 0) + 1
    print(f"Quality tiers: {tiers}")


# ── Direct PDF ingestion ──────────────────────────────────────────────────────

async def direct_ingest(pdf_path: Path, output_dir: Path):
    """Extract all PDFs in pdf_path (file or folder) and write to output_dir.

    Bypasses all search, scoring, and web fetching — reads PDFs from disk directly.
    Applies the same quality filters as the normal pipeline.
    """
    import fitz

    if pdf_path.is_file():
        pdf_files = [pdf_path]
    elif pdf_path.is_dir():
        pdf_files = sorted(pdf_path.glob("*.pdf"))
    else:
        print(f"ERROR: {pdf_path} is not a file or directory.")
        return

    if not pdf_files:
        print(f"No PDFs found at {pdf_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nDirect ingest — {len(pdf_files)} PDF(s) from {pdf_path}")
    print(f"Output: {output_dir}\n")

    async def process_one(path: Path) -> PaperProfileV2 | None:
        print(f"  → Reading: {path.name}")
        try:
            doc = fitz.open(str(path))
            pages = min(40, len(doc))
            text = "\n".join(doc[i].get_text() for i in range(pages))
        except Exception as e:
            print(f"    [error] Could not read PDF: {e}")
            return None

        if len(text.strip()) < 300:
            print(f"    [skip] PDF text too short ({len(text.strip())} chars)")
            return None

        try:
            profile = await _extract_profile_v2(
                text=text,
                research_topic=RESEARCH_TOPIC,
                metadata_model=EXTRACTION_MODEL,
                taxonomy_model=EXTRACTION_MODEL,
                extract_citations=True,
            )
            profile.extraction_status = "full_text"
            profile.source_db = "direct_ingest"
            if not profile.url:
                profile.url = path.stem
            return profile
        except Exception as e:
            print(f"    [error] Extraction failed: {e}")
            return None

    raw = await asyncio.gather(*[process_one(f) for f in pdf_files])

    profiles: list[PaperProfileV2] = []
    dropped_verdict = dropped_year = 0
    for p in raw:
        if p is None:
            continue
        if p.year is not None and p.year < MIN_YEAR:
            print(f"    [year] '{p.title[:60]}' year={p.year} < {MIN_YEAR} — skipping.")
            dropped_year += 1
            continue
        if p.verdict == "no_tool":
            print(f"    [verdict] '{p.title[:60]}' no_tool — skipping.")
            dropped_verdict += 1
            continue
        if p.verdict == "framework_only" and (
            p.quality_tier == "red" or p.study_design == "Qualitative"
        ):
            print(f"    [verdict] '{p.title[:60]}' framework_only+{p.quality_tier} — skipping.")
            dropped_verdict += 1
            continue
        profiles.append(p)

    files = []
    for profile in profiles:
        fname = _write_profile(profile, output_dir)
        files.append(fname)
        print(f"  ✓ {profile.title[:65]}")
        print(f"    verdict={profile.verdict} | tools={[t.name for t in profile.identified_tools]}")
        print(f"    quality={profile.quality_tier} | citations={len(profile.citations)} | file={fname}")

    if profiles:
        _write_summary(profiles, files, output_dir)

    print(f"\n{'='*60}")
    print(f"Done: {len(profiles)} paper(s) written to {output_dir}")
    if dropped_year:
        print(f"      {dropped_year} dropped for year < {MIN_YEAR}")
    if dropped_verdict:
        print(f"      {dropped_verdict} dropped for verdict filter")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-per-query", type=int, default=3,
                        help="Results to fetch per query per DB (default: 3)")
    parser.add_argument("--concurrency", type=int, default=4,
                        help="Max concurrent search requests (default: 4)")
    parser.add_argument("--max-queries", type=int, default=None,
                        help="Cap number of queries for dry-runs (default: all)")
    parser.add_argument("--batch", type=int, default=1, choices=[1, 2],
                        help="Query batch to run: 1=original 51 queries, 2=new 75 queries (default: 1)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Override output directory (default: KG-src/ingested_papers/YYYY-MM-DD)")
    parser.add_argument("--scrape-direct", type=Path, default=None, metavar="PDF_PATH",
                        help="Skip search pipeline — extract PDFs directly from a file or folder")
    args = parser.parse_args()
    if args.output_dir:
        OUTPUT_DIR = args.output_dir
    if args.scrape_direct:
        asyncio.run(direct_ingest(args.scrape_direct, OUTPUT_DIR))
    else:
        asyncio.run(main(args.results_per_query, args.concurrency, args.max_queries, args.batch))

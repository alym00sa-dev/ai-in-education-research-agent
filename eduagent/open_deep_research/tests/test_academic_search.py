"""
Manual test script for ERIC, Semantic Scholar, and OpenAlex tools.

Run from the open_deep_research/src directory:
    cd open_deep_research/src
    python ../tests/test_academic_search.py

Or run a single DB:
    python ../tests/test_academic_search.py eric
    python ../tests/test_academic_search.py semantic
    python ../tests/test_academic_search.py openalex
"""

import asyncio
import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Load .env from open_deep_research root
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from utils.academic_search import eric_search, semantic_scholar_search, openalex_search

# ── Test queries ───────────────────────────────────────────────────────────────

TEST_QUERIES = [
    "RCT intelligent tutoring systems algebra achievement middle school",
    "meta-analysis adaptive learning mathematics K-12 outcomes",
    "reading comprehension intervention English language learners elementary",
    "social emotional learning low income students randomized controlled trial",
]

SEPARATOR = "=" * 80


async def run_test(tool_fn, query: str, db_name: str):
    print(f"\n{SEPARATOR}")
    print(f"DB: {db_name}")
    print(f"Query: {query}")
    print(SEPARATOR)
    try:
        result = await tool_fn.ainvoke({"query": query})
        lines = result.strip().split("\n")
        # Print first 60 lines to keep output readable
        preview = "\n".join(lines[:60])
        print(preview)
        if len(lines) > 60:
            print(f"... [{len(lines) - 60} more lines]")
        # Basic sanity checks
        if "error" in result.lower() and "results" not in result.lower():
            print(f"\n⚠️  Possible error response from {db_name}")
        elif "No results" in result or "No sufficiently relevant" in result:
            print(f"\n⚠️  No relevant results returned")
        else:
            result_count = result.count("[") if "[1]" in result else 0
            print(f"\n✅ {db_name} returned results successfully")
    except Exception as e:
        print(f"\n❌ {db_name} raised exception: {e}")


async def test_eric():
    print(f"\n{'#' * 80}")
    print("TESTING ERIC")
    print(f"{'#' * 80}")
    for q in TEST_QUERIES:
        await run_test(eric_search, q, "ERIC")
        await asyncio.sleep(1)  # Be polite to ERIC (slowest API)


async def test_semantic_scholar():
    print(f"\n{'#' * 80}")
    print("TESTING SEMANTIC SCHOLAR")
    print(f"{'#' * 80}")
    for q in TEST_QUERIES:
        await run_test(semantic_scholar_search, q, "Semantic Scholar")
        await asyncio.sleep(0.5)


async def test_openalex():
    print(f"\n{'#' * 80}")
    print("TESTING OPENALEX")
    print(f"{'#' * 80}")
    for q in TEST_QUERIES:
        await run_test(openalex_search, q, "OpenAlex")
        await asyncio.sleep(0.3)


async def test_all():
    await test_eric()
    await test_semantic_scholar()
    await test_openalex()


if __name__ == "__main__":
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if target == "eric":
        asyncio.run(test_eric())
    elif target in ("semantic", "semantic_scholar"):
        asyncio.run(test_semantic_scholar())
    elif target in ("openalex", "alex"):
        asyncio.run(test_openalex())
    else:
        asyncio.run(test_all())

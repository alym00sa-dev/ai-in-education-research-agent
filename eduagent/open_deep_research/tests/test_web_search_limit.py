"""
Strategic web search experiment.

Compares 4 variants across 2 queries:
  - db_only       : max_web_searches=0, no Tavily at all
  - strategic_5   : max_web_searches=5, web_search_mode=strategic
  - strategic_10  : max_web_searches=10, web_search_mode=strategic
  - unlimited     : no budget, unrestricted mode

Each run saves:
  {stem}_report.md      — final report
  {stem}_meta.json      — timing, source counts, Tavily call count
  {stem}_notes.md       — compressed researcher notes (SOURCES USED/EXCLUDED blocks)
  {stem}_thoughts.json  — full agent thought log (reasoning + tools called per iteration)

Usage (from open_deep_research/ with venv activated):
    python tests/test_web_search_limit.py
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deep_researcher import deep_researcher  # noqa: E402

# ── Config ─────────────────────────────────────────────────────────────────────

QUERIES = [
    "What is the effectiveness of GenAI tools for skill formation primarily focused on high school or secondary school students?",
    "What is the effectiveness of GenAI tools for math achievement in middle school and high school students?",
]

VARIANTS = [
    {"label": "db_only",      "max_web_searches": 0,    "web_search_mode": "unrestricted"},
    {"label": "strategic_5",  "max_web_searches": 5,    "web_search_mode": "strategic"},
    {"label": "strategic_10", "max_web_searches": 10,   "web_search_mode": "strategic"},
    {"label": "unlimited",    "max_web_searches": None, "web_search_mode": "unrestricted"},
]

RESULTS_DIR = Path(__file__).parent / "results"
AUDIT_DIR   = Path(__file__).parent.parent / "audit_logs"

# ── Runner ─────────────────────────────────────────────────────────────────────

async def run_variant(query: str, variant: dict) -> dict:
    label = variant["label"]
    max_ws = variant["max_web_searches"]
    mode   = variant["web_search_mode"]

    print(f"\n{'='*70}")
    print(f"  Query : {query[:75]}...")
    print(f"  Variant: {label}  (max_web_searches={max_ws}, mode={mode})")
    print(f"{'='*70}")

    state_input = {"messages": [{"role": "user", "content": query}]}
    configurable = {
        "research_model": "openai:gpt-4.1",
        "max_researcher_iterations": 5,
        "max_sources": 20,
        "allow_clarification": False,
        "web_search_mode": mode,
    }
    if max_ws is not None:
        configurable["max_web_searches"] = max_ws

    run_start = time.time()
    run_start_utc = datetime.now(timezone.utc)

    result = await deep_researcher.ainvoke(
        state_input,
        config={"configurable": configurable},
    )
    elapsed = time.time() - run_start

    final_report  = result.get("final_report", "")
    notes         = result.get("notes", [])
    thought_log   = result.get("thought_log", [])
    source_counts = result.get("source_counts", {})

    # Count actual Tavily audit files written during this run
    tavily_calls = 0
    if AUDIT_DIR.exists():
        run_start_prefix = run_start_utc.strftime("%Y-%m-%dT%H:%M")
        for af in AUDIT_DIR.iterdir():
            if af.suffix != ".json" or not af.stem.startswith("audit_"):
                continue
            try:
                with open(af) as fh:
                    ad = json.load(fh)
                if ad.get("timestamp", "").startswith(run_start_prefix):
                    tavily_calls += 1
            except Exception:
                pass

    print(f"  Done in {elapsed:.1f}s  |  report: {len(final_report)} chars  |  tavily audit files: {tavily_calls}")
    print(f"  Source counts: {source_counts}")

    return {
        "label": label,
        "query": query,
        "max_web_searches": max_ws,
        "web_search_mode": mode,
        "elapsed_seconds": round(elapsed, 1),
        "report_length_chars": len(final_report),
        "tavily_calls_actual": tavily_calls,
        "source_counts": source_counts,
        "num_thoughts": len(thought_log),
        "final_report": final_report,
        "notes": notes,
        "thought_log": thought_log,
    }


def save_result(result: dict, slug: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{ts}_{slug}"

    # Final report
    report_path = RESULTS_DIR / f"{stem}_report.md"
    report_path.write_text(result["final_report"], encoding="utf-8")

    # Compressed researcher notes (source inclusion log)
    notes = result.get("notes", [])
    if notes:
        notes_text = ("\n\n" + "=" * 60 + "\n\n").join(str(n) for n in notes)
        notes_path = RESULTS_DIR / f"{stem}_notes.md"
        notes_path.write_text(notes_text, encoding="utf-8")

    # Thought log JSON
    thought_log = result.get("thought_log", [])
    if thought_log:
        thoughts_path = RESULTS_DIR / f"{stem}_thoughts.json"
        thoughts_path.write_text(
            json.dumps(thought_log, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # Metadata
    meta = {k: v for k, v in result.items() if k not in ("final_report", "notes", "thought_log")}
    meta["report_file"] = report_path.name
    if notes:
        meta["notes_file"] = f"{stem}_notes.md"
        meta["num_researcher_notes"] = len(notes)
    if thought_log:
        meta["thoughts_file"] = f"{stem}_thoughts.json"
    meta_path = RESULTS_DIR / f"{stem}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"  Saved → {stem}_*")


async def main():
    total = len(QUERIES) * len(VARIANTS)
    print(f"\nStrategic Web Search Experiment")
    print(f"Queries: {len(QUERIES)}  |  Variants: {len(VARIANTS)}  |  Total runs: {total}")

    summary_rows = []

    for q_idx, query in enumerate(QUERIES, 1):
        for variant in VARIANTS:
            slug = f"q{q_idx}_{variant['label']}"
            try:
                result = await run_variant(query, variant)
                save_result(result, slug)
                summary_rows.append({
                    "query":        f"Q{q_idx}",
                    "variant":      variant["label"],
                    "elapsed_s":    result["elapsed_seconds"],
                    "report_chars": result["report_length_chars"],
                    "tavily":       result["tavily_calls_actual"],
                    "source_counts": result["source_counts"],
                    "thoughts":     result["num_thoughts"],
                })
            except Exception as e:
                print(f"  ERROR for {slug}: {e}")
                summary_rows.append({
                    "query":   f"Q{q_idx}",
                    "variant": variant["label"],
                    "error":   str(e),
                })

    # Summary table
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"{'Query':<8} {'Variant':<14} {'Time(s)':<10} {'Chars':<10} {'Tavily':<8} {'Thoughts':<10} Sources")
    print("-" * 80)
    for row in summary_rows:
        if "error" in row:
            print(f"{row['query']:<8} {row['variant']:<14} ERROR: {row['error']}")
        else:
            sc = row.get("source_counts", {})
            sc_str = "  ".join(f"{k}={v}" for k, v in sorted(sc.items()))
            print(
                f"{row['query']:<8} {row['variant']:<14} {row['elapsed_s']:<10} "
                f"{row['report_chars']:<10} {row['tavily']:<8} {row['thoughts']:<10} {sc_str}"
            )

    summary_path = RESULTS_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    print(f"\nSummary saved → {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())

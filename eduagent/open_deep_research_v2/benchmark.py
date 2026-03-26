"""Benchmark runner for autoresearch experiments.

Runs all 4 fixed benchmark queries sequentially, collects QA scores,
and writes results to benchmark_results.tsv.

Usage:
    python -u benchmark.py <experiment_label>

Example:
    python -u benchmark.py baseline
    python -u benchmark.py exp/no-draft-report
"""

import asyncio
import csv
import logging
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage

from graph import graph
from utils.budget import reset_budget

# ---------------------------------------------------------------------------
# Fixed benchmark queries — do NOT modify
# ---------------------------------------------------------------------------

BENCHMARK_QUERIES = [
    (
        "math_tutoring",
        "What is the evidence that tutoring improves math outcomes in K-8 students?",
    ),
    # (
    #     "formative_assessment",
    #     "What is the evidence that formative assessment improves student learning outcomes in K-12?",
    # ),
    (
        "genai_math",
        "What is the evidence that generative AI tools improve math outcomes in K-8 students?",
    ),
    # (
    #     "genai_learning",
    #     "What is the evidence that generative AI tools improve learning outcomes in K-12 classrooms?",
    # ),
]

# ---------------------------------------------------------------------------
# Fixed pipeline config — do NOT modify between experiments
# ---------------------------------------------------------------------------

CONFIG = {
    "configurable": {
        "model": "gpt-5.4-mini",
        "research_iterations": 3,
        "max_concurrent_researchers": 5,
        "max_sweep_cycles": 2,
        "tavily_budget": 5,   # reduced to conserve API budget during experiments
        "serp_budget": 0,     # disabled during experiments
        "enable_pdf_extraction": True,
        "max_sources": 30,
    },
    "recursion_limit": 200,
}

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "benchmark_results.tsv")
FLOOR_SCORE = 55  # Any single query below this = experiment fails regardless of average


async def run_query(label: str, query: str, experiment_label: str, out_dir: str) -> int:
    """Run a single benchmark query, save final report + QA audit, return QA score."""
    print(f"\n  [{label}] Starting: {query[:70]}...")
    start = time.time()

    tavily_limit = CONFIG["configurable"].get("tavily_budget", 5)
    serp_limit = CONFIG["configurable"].get("serp_budget", 0)
    reset_budget(tavily_limit=tavily_limit, serp_limit=serp_limit)

    input_state = {"messages": [HumanMessage(content=query)]}
    final_state = None
    async for chunk in graph.astream(input_state, CONFIG, stream_mode="values"):
        final_state = chunk

    elapsed = time.time() - start
    score = final_state.get("qa_score", 0) if final_state else 0

    # Save final report and QA audit
    slug = experiment_label.replace("/", "_").replace(" ", "_").replace(":", "")
    prefix = os.path.join(out_dir, f"{slug}__{label}")

    final_report = (final_state or {}).get("final_report", "")
    qa_report = (final_state or {}).get("qa_report", "")

    if final_report:
        run_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"# Benchmark: {experiment_label} — {label}\n\n"
            f"**Query:** {query}\n\n"
            f"**Date/Time:** {run_datetime}\n\n"
            f"**QA Score:** {score}/100\n\n"
            "---\n\n"
        )
        with open(f"{prefix}__final_report.md", "w") as f:
            f.write(header + final_report)

    if qa_report:
        with open(f"{prefix}__qa_report.md", "w") as f:
            f.write(f"# QA Audit: {experiment_label} — {label}\n\n"
                    f"**Score: {score}/100**\n\n---\n\n" + qa_report)

    print(f"  [{label}] Done in {elapsed:.0f}s — QA score: {score}/100")
    return score


async def main():
    if len(sys.argv) < 2:
        print("Usage: python -u benchmark.py <experiment_label>")
        sys.exit(1)

    experiment_label = " ".join(sys.argv[1:])
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"Benchmark Run: {experiment_label}")
    print(f"Time: {timestamp}")
    print(f"Queries: {len(BENCHMARK_QUERIES)}")
    print(f"{'='*60}")

    out_dir = os.path.join(os.path.dirname(__file__), "benchmark_output")
    os.makedirs(out_dir, exist_ok=True)

    scores: dict[str, int] = {}
    for label, query in BENCHMARK_QUERIES:
        score = await run_query(label, query, experiment_label, out_dir)
        scores[label] = score

    # Compute average
    avg = sum(scores.values()) / len(scores)
    min_score = min(scores.values())
    passed_floor = min_score >= FLOOR_SCORE
    status = "KEEP" if passed_floor else "FLOOR_FAIL"

    # Print summary
    print(f"\n{'='*60}")
    print(f"Experiment : {experiment_label}")
    print(f"Scores     : {scores}")
    print(f"Average    : {avg:.1f}/100")
    print(f"Min score  : {min_score}/100 (floor={FLOOR_SCORE})")
    print(f"Status     : {status}")
    print(f"{'='*60}\n")

    # Write to results TSV
    file_exists = os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        if not file_exists:
            writer.writerow([
                "timestamp", "experiment",
                "math_tutoring", "formative_assessment", "genai_math", "genai_learning",
                "average", "min_score", "status",
            ])
        writer.writerow([
            timestamp,
            experiment_label,
            scores.get("math_tutoring", 0),
            scores.get("formative_assessment", 0),
            scores.get("genai_math", 0),
            scores.get("genai_learning", 0),
            f"{avg:.1f}",
            min_score,
            status,
        ])

    print(f"Results appended to: {RESULTS_FILE}")
    return avg


if __name__ == "__main__":
    asyncio.run(main())

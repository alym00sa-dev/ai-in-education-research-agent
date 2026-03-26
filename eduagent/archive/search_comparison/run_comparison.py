"""
Search API Comparison — run all 5 searchers across all test queries,
score results with Claude, and write a markdown report.

Usage:
    python run_comparison.py                  # run all searchers + queries
    python run_comparison.py --searchers exa brave   # run specific searchers only
    python run_comparison.py --no-eval        # skip LLM scoring (faster)
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pathlib import Path

# Load local .env first, then fall back to the main app .env for shared keys
_here = Path(__file__).parent
load_dotenv(_here / ".env")
load_dotenv(_here.parent / "research_assistant_agent" / ".env")

from config import TEST_QUERIES
from searchers import ALL_SEARCHERS
from searchers.base import SearchResponse
from evaluate import score_response


# ── Run all searchers in parallel ─────────────────────────────────────────────

def run_all(searcher_names: list[str], queries: list[str]) -> list[SearchResponse]:
    tasks = [
        (name, query)
        for name in searcher_names
        for query in queries
    ]
    results = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        futures = {
            pool.submit(ALL_SEARCHERS[name], query): (name, query)
            for name, query in tasks
        }
        for future in as_completed(futures):
            name, query = futures[future]
            try:
                result = future.result()
            except Exception as e:
                from searchers.base import SearchResponse
                result = SearchResponse(searcher=name, query=query, error=str(e))
            print(f"  {'✓' if not result.error else '✗'} {name:10s} | {query[:60]}")
            results.append(result)
    return results


# ── Score results ──────────────────────────────────────────────────────────────

def score_all(responses: list[SearchResponse]) -> dict:
    """Returns {searcher: {query: scores_dict}}"""
    scores = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(score_response, r): r for r in responses}
        for future in as_completed(futures):
            r = futures[future]
            scores.setdefault(r.searcher, {})[r.query] = future.result()
    return scores


# ── Report generation ──────────────────────────────────────────────────────────

def _avg(values):
    return round(sum(values) / len(values), 2) if values else 0


def build_report(responses: list[SearchResponse], scores: dict, out_dir: Path) -> str:
    lines = [
        "# Search API Comparison Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Queries Tested",
    ]
    for i, q in enumerate(TEST_QUERIES, 1):
        lines.append(f"{i}. {q}")
    lines.append("")

    # ── Per-query breakdown ────────────────────────────────────────────────────
    lines.append("## Results by Query\n")
    query_to_responses: dict[str, list[SearchResponse]] = {}
    for r in responses:
        query_to_responses.setdefault(r.query, []).append(r)

    for query, qresps in query_to_responses.items():
        lines.append(f"### Query: *{query}*\n")
        lines.append("| Searcher | Results | Latency (s) | Academic % | Avg Snippet | Relevance | Source Quality | Snippet Usefulness | Reasoning |")
        lines.append("|----------|---------|-------------|------------|-------------|-----------|----------------|--------------------|-----------|")
        for r in sorted(qresps, key=lambda x: x.searcher):
            sc = (scores.get(r.searcher) or {}).get(r.query) or {}
            error_note = f" ⚠ {r.error}" if r.error else ""
            lines.append(
                f"| {r.searcher} "
                f"| {len(r.results)}{error_note} "
                f"| {r.latency_s} "
                f"| {round(r.academic_ratio * 100)}% "
                f"| {r.avg_snippet_length} chars "
                f"| {sc.get('relevance', '-')} "
                f"| {sc.get('source_quality', '-')} "
                f"| {sc.get('snippet_usefulness', '-')} "
                f"| {sc.get('reasoning', '')} |"
            )
        lines.append("")

        # Top sources per searcher
        for r in sorted(qresps, key=lambda x: x.searcher):
            if r.results:
                lines.append(f"<details><summary>{r.searcher} — top sources</summary>\n")
                for res in r.results[:5]:
                    lines.append(f"- [{res.title}]({res.url})  ")
                    if res.snippet:
                        lines.append(f"  > {res.snippet[:200]}")
                lines.append("\n</details>\n")

    # ── Aggregate summary ──────────────────────────────────────────────────────
    lines.append("## Aggregate Summary\n")
    lines.append("| Searcher | Avg Relevance | Avg Source Quality | Avg Snippet Usefulness | Avg Latency (s) | Avg Academic % |")
    lines.append("|----------|---------------|--------------------|------------------------|-----------------|----------------|")

    searcher_names = sorted(ALL_SEARCHERS.keys())
    for name in searcher_names:
        searcher_resps = [r for r in responses if r.searcher == name]
        searcher_scores = scores.get(name, {})
        avg_rel = _avg([v.get("relevance", 0) for v in searcher_scores.values()])
        avg_sq = _avg([v.get("source_quality", 0) for v in searcher_scores.values()])
        avg_su = _avg([v.get("snippet_usefulness", 0) for v in searcher_scores.values()])
        avg_lat = _avg([r.latency_s for r in searcher_resps])
        avg_acad = _avg([r.academic_ratio * 100 for r in searcher_resps])
        lines.append(
            f"| {name} | {avg_rel} | {avg_sq} | {avg_su} | {avg_lat} | {round(avg_acad)}% |"
        )

    lines.append("")
    report = "\n".join(lines)

    # Write files
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.md").write_text(report)
    raw = [
        {
            "searcher": r.searcher,
            "query": r.query,
            "latency_s": r.latency_s,
            "num_results": len(r.results),
            "academic_ratio": r.academic_ratio,
            "results": [{"title": x.title, "url": x.url, "snippet": x.snippet} for x in r.results],
            "llm_answer": r.llm_answer,
            "error": r.error,
            "scores": (scores.get(r.searcher) or {}).get(r.query),
        }
        for r in responses
    ]
    (out_dir / "raw_results.json").write_text(json.dumps(raw, indent=2))
    return report


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--searchers", nargs="+", choices=list(ALL_SEARCHERS.keys()),
                        default=list(ALL_SEARCHERS.keys()))
    parser.add_argument("--no-eval", action="store_true", help="Skip LLM scoring")
    args = parser.parse_args()

    out_dir = Path(__file__).parent / "results" / datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\nRunning {len(args.searchers)} searchers × {len(TEST_QUERIES)} queries...\n")
    responses = run_all(args.searchers, TEST_QUERIES)

    scores = {}
    if not args.no_eval:
        print("\nScoring results with Claude Haiku...\n")
        scores = score_all(responses)

    report = build_report(responses, scores, out_dir)

    print(f"\nReport saved to: {out_dir}/report.md")
    print(f"Raw data:        {out_dir}/raw_results.json\n")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()

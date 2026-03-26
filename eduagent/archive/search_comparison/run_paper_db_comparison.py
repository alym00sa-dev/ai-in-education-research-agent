"""
Paper Database Comparison — OpenAlex, ERIC, Semantic Scholar.

Usage:
    python run_paper_db_comparison.py
    python run_paper_db_comparison.py --no-eval
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

_here = Path(__file__).parent
load_dotenv(_here / ".env")
load_dotenv(_here.parent / "research_assistant_agent" / ".env")

from config import TEST_QUERIES
from searchers import PAPER_DB_SEARCHERS
from searchers.base import SearchResponse
from evaluate import score_response


_RATE_LIMITED = {"semantic_scholar"}  # run sequentially with a delay


def run_all(queries: list[str]) -> list[SearchResponse]:
    results = []

    # Parallel searchers
    parallel_tasks = [
        (name, query)
        for name in PAPER_DB_SEARCHERS
        for query in queries
        if name not in _RATE_LIMITED
    ]
    with ThreadPoolExecutor(max_workers=len(parallel_tasks) or 1) as pool:
        futures = {
            pool.submit(PAPER_DB_SEARCHERS[name], query): (name, query)
            for name, query in parallel_tasks
        }
        for future in as_completed(futures):
            name, query = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = SearchResponse(searcher=name, query=query, error=str(e))
            print(f"  {'✓' if not result.error else '✗'} {name:20s} | {query[:55]}")
            results.append(result)

    # Sequential searchers (rate-limited)
    for name in _RATE_LIMITED:
        if name not in PAPER_DB_SEARCHERS:
            continue
        for i, query in enumerate(queries):
            if i == 0:
                print(f"  (waiting 10s before {name} to respect rate limit...)")
                time.sleep(10)
            else:
                print(f"  (waiting 5s for {name} rate limit...)")
                time.sleep(5)
            try:
                result = PAPER_DB_SEARCHERS[name](query)
            except Exception as e:
                result = SearchResponse(searcher=name, query=query, error=str(e))
            print(f"  {'✓' if not result.error else '✗'} {name:20s} | {query[:55]}")
            results.append(result)

    return results


def score_all(responses: list[SearchResponse]) -> dict:
    scores = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(score_response, r): r for r in responses}
        for future in as_completed(futures):
            r = futures[future]
            scores.setdefault(r.searcher, {})[r.query] = future.result()
    return scores


def _avg(values):
    return round(sum(values) / len(values), 2) if values else 0


def build_report(responses: list[SearchResponse], scores: dict, out_dir: Path) -> str:
    lines = [
        "# Paper Database Comparison Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Databases Tested",
        "- **OpenAlex** — 250M+ works, free, no key required",
        "- **ERIC** — US Dept of Education, education-specific, free",
        "- **Semantic Scholar** — AI2, 225M+ papers, AI-powered, free",
        "",
        "## Queries Tested",
    ]
    for i, q in enumerate(TEST_QUERIES, 1):
        lines.append(f"{i}. {q}")
    lines.append("")

    # Per-query breakdown
    lines.append("## Results by Query\n")
    query_to_responses: dict[str, list[SearchResponse]] = {}
    for r in responses:
        query_to_responses.setdefault(r.query, []).append(r)

    for query, qresps in query_to_responses.items():
        lines.append(f"### Query: *{query}*\n")
        lines.append("| DB | Results | Latency (s) | Academic % | Avg Snippet | Relevance | Source Quality | Snippet Usefulness | Notes |")
        lines.append("|----|---------|-------------|------------|-------------|-----------|----------------|--------------------|-------|")
        for r in sorted(qresps, key=lambda x: x.searcher):
            sc = (scores.get(r.searcher) or {}).get(r.query) or {}
            error_note = f"⚠ {r.error}" if r.error else sc.get("reasoning", "")
            lines.append(
                f"| {r.searcher} "
                f"| {len(r.results)} "
                f"| {r.latency_s} "
                f"| {round(r.academic_ratio * 100)}% "
                f"| {r.avg_snippet_length} chars "
                f"| {sc.get('relevance', '-')} "
                f"| {sc.get('source_quality', '-')} "
                f"| {sc.get('snippet_usefulness', '-')} "
                f"| {error_note[:120]} |"
            )
        lines.append("")

        # Top results per DB
        for r in sorted(qresps, key=lambda x: x.searcher):
            if r.results:
                lines.append(f"<details><summary>{r.searcher} — top results</summary>\n")
                for res in r.results[:5]:
                    lines.append(f"- **{res.title}**")
                    lines.append(f"  {res.url}")
                    if res.snippet:
                        lines.append(f"  > {res.snippet[:300]}")
                    lines.append("")
                lines.append("</details>\n")

    # Aggregate summary
    lines.append("## Aggregate Summary\n")
    lines.append("| DB | Avg Relevance | Avg Source Quality | Avg Snippet Usefulness | Avg Latency (s) | Avg Academic % |")
    lines.append("|----|---------------|--------------------|------------------------|-----------------|----------------|")
    for name in sorted(PAPER_DB_SEARCHERS.keys()):
        searcher_resps = [r for r in responses if r.searcher == name]
        sc = scores.get(name, {})
        lines.append(
            f"| {name} "
            f"| {_avg([v.get('relevance', 0) for v in sc.values()])} "
            f"| {_avg([v.get('source_quality', 0) for v in sc.values()])} "
            f"| {_avg([v.get('snippet_usefulness', 0) for v in sc.values()])} "
            f"| {_avg([r.latency_s for r in searcher_resps])} "
            f"| {round(_avg([r.academic_ratio * 100 for r in searcher_resps]))}% |"
        )

    lines.append("")
    report = "\n".join(lines)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "paper_db_report.md").write_text(report)
    raw = [
        {
            "searcher": r.searcher,
            "query": r.query,
            "latency_s": r.latency_s,
            "num_results": len(r.results),
            "academic_ratio": r.academic_ratio,
            "avg_snippet_length": r.avg_snippet_length,
            "results": [{"title": x.title, "url": x.url, "snippet": x.snippet} for x in r.results],
            "error": r.error,
            "scores": (scores.get(r.searcher) or {}).get(r.query),
        }
        for r in responses
    ]
    (out_dir / "paper_db_raw.json").write_text(json.dumps(raw, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-eval", action="store_true")
    args = parser.parse_args()

    out_dir = Path(__file__).parent / "results" / datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\nRunning {len(PAPER_DB_SEARCHERS)} paper DBs × {len(TEST_QUERIES)} queries...\n")
    responses = run_all(TEST_QUERIES)

    scores = {}
    if not args.no_eval:
        print("\nScoring with Claude Haiku...\n")
        scores = score_all(responses)

    report = build_report(responses, scores, out_dir)

    print(f"\nReport: {out_dir}/paper_db_report.md")
    print(f"Raw:    {out_dir}/paper_db_raw.json\n")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()

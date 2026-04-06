"""Quick test runner for the end to end deep research pipeline testing -- locally."""

import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "deep-research-src"))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage

from graph import graph


class _Tee:
    """Write to both the original stream and a log file with elapsed-time prefixes."""
    def __init__(self, stream, filepath, start: float):
        self._stream = stream
        self._file = open(filepath, "w", buffering=1)
        self._start = start
        self._at_line_start = True

    def _elapsed(self) -> str:
        e = int(time.time() - self._start)
        m, s = divmod(e, 60)
        return f"[+{m}m{s:02d}s] "

    def write(self, data):
        self._stream.write(data)
        if not data:
            return
        stamped = []
        for ch in data:
            if self._at_line_start and ch != "\n":
                stamped.append(self._elapsed())
                self._at_line_start = False
            stamped.append(ch)
            if ch == "\n":
                self._at_line_start = True
        self._file.write("".join(stamped))

    def flush(self):
        self._stream.flush()
        self._file.flush()

    def fileno(self):
        return self._stream.fileno()

    def close(self):
        self._file.close()


# Set up persistent log in deep-research-output/final-test/
_LOG_DIR = os.path.join(os.path.dirname(__file__), "deep-research-output", "final-test")
os.makedirs(_LOG_DIR, exist_ok=True)


_DEFAULT_QUERY = (
    "What is the impact of medical treatment of ADHD on scholastic achievement "
    "during K-5 (kindergarten through 5th grade)?"
)

# Accept query from CLI: python run_pipeline.py "your query here"
QUERY = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else _DEFAULT_QUERY

CONFIG = {
    "configurable": {
        "model": "openai:gpt-5.4-mini-2026-03-17",
        "report_model": "openai:gpt-5.4-2026-03-05",
        "research_iterations": 3,
        "max_concurrent_researchers": 5,
        "max_sweep_cycles": 2,
        "tavily_budget": 8,
        "serp_budget": 2,
        "enable_pdf_extraction": True,
        "max_sources": 30,
    },
    "recursion_limit": 200,
}


def _ts(start: float) -> str:
    elapsed = int(time.time() - start)
    m, s = divmod(elapsed, 60)
    return f"+{m}m{s:02d}s"


async def main():
    # Create a per-run subfolder inside deep-research-output/final-test/
    _slug = "_".join(QUERY.split()[:6]).lower()
    _slug = "".join(c if c.isalnum() or c == "_" else "" for c in _slug)
    _run_id = f"{_slug}_{time.strftime('%Y%m%d_%H%M%S')}"
    _run_dir = os.path.join(_LOG_DIR, _run_id)
    os.makedirs(_run_dir, exist_ok=True)

    start = time.time()

    # Wire persistent log file into the run subfolder
    _log_path = os.path.join(_run_dir, "run.log")
    _tee = _Tee(sys.stdout, _log_path, start)
    sys.stdout = _tee
    print(f"[run_pipeline] Run folder: {_run_dir}", flush=True)

    print(f"\n{'='*60}")
    print("Deep Research v2 — Test Run")
    print(f"Query: {QUERY[:80]}...")
    print(f"{'='*60}\n")

    # Budget reset now happens inside education_discovery node using config values
    input_state = {"messages": [HumanMessage(content=QUERY)]}
    stage_times: dict[str, float] = {}

    # Track previous values to avoid duplicate prints on re-emitted state
    seen = {
        "research_brief": False,
        "compress_count": 0,
        "draft_count": 0,
        "critique_count": 0,
        "notes_count": 0,
        "profiles_count": 0,
        "final_report": False,
    }

    final_state = None
    async for chunk in graph.astream(input_state, CONFIG, stream_mode="values"):
        final_state = chunk
        t = _ts(start)

        # education_discovery
        if chunk.get("research_brief") and not seen["research_brief"]:
            seen["research_brief"] = True
            stage_times["discovery"] = time.time()
            print(f"[{t}] [education_discovery] Research brief ready.")
            brief = chunk["research_brief"]
            for line in brief.split("\n")[:4]:
                if line.strip():
                    print(f"          {line.strip()}")

        # researcher notes arriving (proxy for researcher completion)
        notes = chunk.get("notes", [])
        if len(notes) > seen["notes_count"]:
            new = len(notes) - seen["notes_count"]
            seen["notes_count"] = len(notes)
            print(f"[{t}] [researcher] {new} new thread(s) completed — {len(notes)} total notes")

        # paper profiles
        profiles = chunk.get("paper_profiles", [])
        if len(profiles) > seen["profiles_count"]:
            seen["profiles_count"] = len(profiles)
            print(f"[{t}] [pdf_extractor] {len(profiles)} paper profiles so far")

        # compress_findings
        compress_hist = chunk.get("compress_findings_history", [])
        if len(compress_hist) > seen["compress_count"]:
            seen["compress_count"] = len(compress_hist)
            stage_times[f"compress_{len(compress_hist)}"] = time.time()
            print(f"[{t}] [compress_findings] Iteration {len(compress_hist)} evidence summary ready.")

        # draft_report
        draft_hist = chunk.get("draft_report_history", [])
        if len(draft_hist) > seen["draft_count"]:
            seen["draft_count"] = len(draft_hist)
            stage_times[f"draft_{len(draft_hist)}"] = time.time()
            print(f"[{t}] [draft_report] Iteration {len(draft_hist)} draft ready.")

        # critique
        critique_hist = chunk.get("critique_history", [])
        if len(critique_hist) > seen["critique_count"]:
            seen["critique_count"] = len(critique_hist)
            stage_times[f"critique_{len(critique_hist)}"] = time.time()
            print(f"[{t}] [critique] Iteration {len(critique_hist)} critique ready.")

        # final report
        if chunk.get("final_report") and not seen["final_report"]:
            seen["final_report"] = True
            stage_times["final"] = time.time()
            print(f"[{t}] [final_report] Final report generated.")

        # qa audit
        if chunk.get("qa_report") and not seen.get("qa_report"):
            seen["qa_report"] = True
            stage_times["qa"] = time.time()
            score = chunk.get("qa_score", 0)
            print(f"[{t}] [qa_audit] QA audit complete. Score: {score}/100")

    if not final_state:
        print("ERROR: No state returned.")
        return

    total = time.time() - start

    # Write outputs
    out_dir = _run_dir  # deep-research-output/final-test/<run_id>/
    os.makedirs(out_dir, exist_ok=True)

    # Build a filename slug from the query (first 6 words, underscored)
    slug = "_".join(QUERY.split()[:6]).lower()
    slug = "".join(c if c.isalnum() or c == "_" else "" for c in slug)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_id = f"{slug}_{timestamp}"

    report = final_state.get("final_report", "")
    if report:
        report_path = os.path.join(out_dir, f"final_report_{run_id}.md")
        run_number = run_id  # slug_YYYYMMDD_HHMMSS
        run_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"# Research Run: {run_number}\n\n"
            f"**Query:** {QUERY}\n\n"
            f"**Date/Time:** {run_datetime}\n\n"
            "---\n\n"
        )
        with open(report_path, "w") as f:
            f.write(header + report)
        print(f"\nFinal report saved to: {report_path}")

    qa = final_state.get("qa_report", "")
    if qa:
        qa_path = os.path.join(out_dir, f"qa_report_{run_id}.md")
        with open(qa_path, "w") as f:
            f.write(qa)
        print(f"QA audit saved to: {qa_path}")

    def _serialize(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return str(obj)

    snapshot = {
        k: v for k, v in final_state.items()
        if k not in ("messages", "supervisor_messages", "researcher_messages")
    }
    snapshot_path = os.path.join(out_dir, f"state_snapshot_{run_id}.json")
    with open(snapshot_path, "w") as f:
        json.dump(snapshot, f, indent=2, default=_serialize)
    print(f"State snapshot saved to: {snapshot_path}")

    # Filter stats
    filter_log = final_state.get("filtered_papers_log", [])
    passed = sum(1 for e in filter_log if e.get("decision") == "PASS")
    dropped = sum(1 for e in filter_log if e.get("decision") == "DROP")
    by_tool: dict[str, dict] = {}
    for e in filter_log:
        tool = e.get("tool", "unknown")
        if tool not in by_tool:
            by_tool[tool] = {"pass": 0, "drop": 0}
        by_tool[tool]["pass" if e.get("decision") == "PASS" else "drop"] += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Total time           : {total:.1f}s")
    print(f"Iterations completed : {final_state.get('iteration', 0) + 1}")
    print(f"Notes collected      : {len(final_state.get('all_notes', []))}")
    print(f"Paper profiles       : {len(final_state.get('paper_profiles', []))}")
    print(f"QA score             : {final_state.get('qa_score', 0)}/100")
    print(f"Source counts        : {final_state.get('source_counts', {})}")

    if filter_log:
        print(f"\nPaper filter         : {passed} passed, {dropped} dropped")
        for tool, counts in sorted(by_tool.items()):
            print(f"  {tool:<35} pass={counts['pass']}  drop={counts['drop']}")

    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())

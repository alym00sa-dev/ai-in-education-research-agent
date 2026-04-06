"""Save pipeline run outputs to deep-research-output/final-test/<session_id>/."""

import json
import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import AgentState

_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "deep-research-output"
)


def _serialize(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return str(obj)


def save_run_output(session_id: str, state: dict, qa_report: str, run_config: dict | None = None) -> str:
    """Save final_report, qa_report, and state_snapshot to deep-research-output/final-test/<session_id>/.

    Returns the run directory path.
    """
    run_dir = os.path.join(_OUTPUT_DIR, session_id)
    os.makedirs(run_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Extract query from messages
    messages = state.get("messages", [])
    query = ""
    if messages:
        first = messages[0]
        if hasattr(first, "content"):
            query = str(first.content)
        elif isinstance(first, dict):
            query = str(first.get("content", ""))

    # Save final report
    final_report = state.get("final_report", "")
    if final_report:
        header = (
            f"# Research Run: {session_id}\n\n"
            f"**Query:** {query}\n\n"
            f"**Date/Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "---\n\n"
        )
        report_path = os.path.join(run_dir, f"final_report_{timestamp}.md")
        with open(report_path, "w") as f:
            f.write(header + final_report)

    # Save QA report
    if qa_report:
        qa_path = os.path.join(run_dir, f"qa_report_{timestamp}.md")
        with open(qa_path, "w") as f:
            f.write(qa_report)

    # Save full state snapshot — same structure as CLI run_pipeline.py output
    paper_profiles = state.get("paper_profiles", [])
    snapshot = {
        "session_id": session_id,
        "run_config": run_config or {},
        "research_brief": state.get("research_brief", ""),
        "tiered_question_map": state.get("tiered_question_map", {}),
        "iteration": state.get("iteration", 0),
        "executive_summary_history": state.get("executive_summary_history", []),
        "critique_history": state.get("critique_history", []),
        "notes": state.get("notes", []),
        "raw_notes": state.get("raw_notes", []),
        "all_notes": state.get("all_notes", []),
        "final_report": state.get("final_report", ""),
        "qa_report": state.get("qa_report", ""),
        "qa_score": state.get("qa_score", 0),
        "paper_profiles": [_serialize(p) for p in paper_profiles],
        "source_counts": state.get("source_counts", {}),
        "thought_log": state.get("thought_log", []),
        "filtered_papers_log": state.get("filtered_papers_log", []),
        "run_graph_analysis": state.get("run_graph_analysis", {}),
        "run_graph_section": state.get("run_graph_section", ""),
    }
    snap_path = os.path.join(run_dir, f"state_snapshot_{timestamp}.json")
    with open(snap_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"[output_saver] Run saved → {run_dir}", flush=True)
    return run_dir

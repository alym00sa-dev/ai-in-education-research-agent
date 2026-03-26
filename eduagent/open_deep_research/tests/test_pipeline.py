"""Pipeline decomposition test — education_discovery → supervisor dispatch.

Tests ONLY the decomposition step:
  1. education_discovery: user query → research brief
  2. supervisor: research brief → think reflections + sub-questions dispatched

Researchers are mocked — no real searches run, no cost.
Traces to Phoenix at http://localhost:6006 (project: discovery-test).
Saves a JSON per query to tests/output/<timestamp>_q<n>.json.

Usage:
    cd eduagent/open_deep_research
    source .venv/bin/activate
    phoenix serve            # Terminal 1
    python tests/test_pipeline.py   # Terminal 2
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.tracing import setup_tracing
setup_tracing(project_name="discovery-test")

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from deep_researcher import deep_researcher

# ── Queries ────────────────────────────────────────────────────────────────────

QUERIES = [
    "What does the research say about the effectiveness of high-dosage tutoring on math outcomes for K-8 students?",
    "What does the research say about the effectiveness of AI-powered tutoring systems on student learning outcomes in K–12 mathematics?",
    "What does the research say about the effects of generative AI tools (e.g., ChatGPT, Copilot) on skill formation and learning outcomes among college students?",
    "What does the research say about the effectiveness of active learning approaches in undergraduate STEM courses?",
]

OUTPUT_DIR = Path(__file__).parent / "output"

# ── Mock researcher — returns topic immediately, no searching ──────────────────

async def mock_researcher(inputs: dict, config=None) -> dict:
    """Stub that echoes back the research topic without doing any work."""
    topic = inputs.get("research_topic", "")
    return {
        "compressed_research": f"[MOCK] Would research: {topic}",
        "raw_notes": [],
        "thought_log": [],
        "source_counts": {},
    }

# ── State parser ───────────────────────────────────────────────────────────────

def parse_supervisor_messages(supervisor_messages: list) -> list[dict]:
    """Reconstruct supervisor iterations from the raw message list."""
    iterations = []

    # Build lookup: tool_call_id → ToolMessage content
    tool_results: dict[str, str] = {}
    for msg in supervisor_messages:
        if isinstance(msg, ToolMessage):
            tool_results[msg.tool_call_id] = msg.content

    for msg in supervisor_messages:
        if not isinstance(msg, AIMessage) or not msg.tool_calls:
            continue

        think_reflections = []
        dispatched = []
        research_complete = False

        for tc in msg.tool_calls:
            if tc["name"] == "think_tool":
                think_reflections.append(tc["args"].get("reflection", ""))
            elif tc["name"] == "ConductResearch":
                topic = tc["args"].get("research_topic", "")
                keywords = tc["args"].get("keywords", [])
                dispatched.append({"research_topic": topic, "keywords": keywords})
            elif tc["name"] == "ResearchComplete":
                research_complete = True

        if think_reflections or dispatched or research_complete:
            iterations.append({
                "iteration": len(iterations) + 1,
                "think_reflections": think_reflections,
                "researchers_dispatched": dispatched,
                "research_complete_called": research_complete,
            })

    return iterations


def build_run_log(query: str, state: dict, elapsed_s: float) -> dict:
    supervisor_messages = state.get("supervisor_messages", [])
    if isinstance(supervisor_messages, dict):
        supervisor_messages = supervisor_messages.get("value", [])

    iterations = parse_supervisor_messages(supervisor_messages)

    return {
        "query": query,
        "research_brief": state.get("research_brief", ""),
        "elapsed_seconds": round(elapsed_s, 1),
        "total_supervisor_iterations": len(iterations),
        "supervisor_iterations": iterations,
    }

# ── Printer ────────────────────────────────────────────────────────────────────

def print_run_summary(log: dict, query_idx: int) -> None:
    print(f"\n{'='*70}")
    print(f"Query {query_idx}: {log['query'][:80]}{'...' if len(log['query']) > 80 else ''}")
    print(f"{'='*70}")
    print(f"\n  Research brief:\n  {log['research_brief']}")
    print(f"\n  Elapsed: {log['elapsed_seconds']}s  |  Supervisor iterations: {log['total_supervisor_iterations']}")

    for it in log["supervisor_iterations"]:
        print(f"\n  ── Iteration {it['iteration']} ──")
        for ref in it["think_reflections"]:
            print(f"    [think] {ref[:200]}{'...' if len(ref) > 200 else ''}")
        for r in it["researchers_dispatched"]:
            print(f"    [dispatch] {r['research_topic']}")
            if r.get("keywords"):
                print(f"             keywords: {', '.join(r['keywords'])}")
        if it["research_complete_called"]:
            print(f"    [ResearchComplete]")

# ── Runner ─────────────────────────────────────────────────────────────────────

async def run_query(query: str, query_idx: int) -> dict:
    print(f"\n[Q{query_idx}] {query[:70]}...")
    start = datetime.now()

    config = {
        "configurable": {
            "allow_clarification": False,
            "max_researcher_iterations": 1,   # one supervisor round only
            "max_concurrent_research_units": 6,
        }
    }

    with patch("nodes.supervisor.researcher_subgraph") as mock_graph:
        mock_graph.ainvoke = mock_researcher
        state = await deep_researcher.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config=config,
        )

    elapsed = (datetime.now() - start).total_seconds()
    return build_run_log(query, state, elapsed)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Decomposition test — {len(QUERIES)} queries (researchers mocked)")
    print("Traces → http://localhost:6006  (project: discovery-test)")
    print(f"Output → {OUTPUT_DIR}/")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, query in enumerate(QUERIES, 1):
        log = await run_query(query, i)
        print_run_summary(log, i)

        out_path = OUTPUT_DIR / f"{timestamp}_q{i}_decomp.json"
        with open(out_path, "w") as f:
            json.dump(log, f, indent=2)
        print(f"\n  Saved → {out_path.name}")

    print(f"\n{'='*70}")
    print(f"Done. JSONs in {OUTPUT_DIR}/")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())

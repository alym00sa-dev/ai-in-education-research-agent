"""
Direct pipeline runner with full verbose stdout logging.
Tracks every stage: education_discovery → supervisor → researchers → critique → report

Usage: python run_pipeline.py
"""
import asyncio
import os
import sys
import traceback
from datetime import datetime

# Force line-buffered stdout so output appears immediately when redirected to a file
sys.stdout.reconfigure(line_buffering=True)

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.deep_researcher import deep_researcher

QUERY = (
    "what is the effectiveness of GenAI tools for skill formation "
    "primarily focused on high school or secondary school students in the US?"
)

_ITERATIONS = int(os.environ.get("RESEARCH_ITERATIONS", 2))  # override: RESEARCH_ITERATIONS=3 python run_pipeline.py

CONFIG = {
    "configurable": {
        "research_model":                "openai:gpt-4.1",
        "search_api":                    "openai",
        "allow_clarification":           False,
        "research_iterations":           _ITERATIONS,             # critique cycles = iterations - 1
        "max_researcher_iterations":     6,
        "max_react_tool_calls":          40,
        "tavily_budget":                 10,
        "serpapi_budget":                3,
        "max_sources":                   30,
        "enable_pdf_extraction":         True,
        "max_concurrent_research_units": 5,
    },
    "recursion_limit": 200,   # default 25 is too low for parallel researcher loops
}

# ── helpers ────────────────────────────────────────────────────────────────────

def ts():
    return datetime.now().strftime("%H:%M:%S")

def elapsed(start: datetime) -> str:
    s = int((datetime.now() - start).total_seconds())
    return f"{s//60}m{s%60:02d}s"

def hr(char="─", n=72):
    print(char * n, flush=True)

def section(title: str):
    print()
    hr("═")
    print(f"  {title}", flush=True)
    hr("═")

def subsection(title: str):
    print()
    hr()
    print(f"  {title}", flush=True)
    hr()

# ── main ───────────────────────────────────────────────────────────────────────

async def run():
    start = datetime.now()

    section(f"PIPELINE START  [{ts()}]")
    print(f"  query  : {QUERY}")
    print(f"  model  : {CONFIG['configurable']['research_model']}")
    print(f"  iters  : {CONFIG['configurable']['research_iterations']} (critique cycles: {CONFIG['configurable']['research_iterations'] - 1})")
    print(f"  pdf    : {CONFIG['configurable']['enable_pdf_extraction']}")
    print()

    state_input = {"messages": [{"role": "user", "content": QUERY}]}

    # ── tracking state ─────────────────────────────────────────────────────────
    prev_note_count    = 0
    prev_paper_count   = 0
    prev_sup_msg_count = 0
    seen_stages        = set()

    # tool call counter from events
    tool_call_counts: dict[str, int] = {}

    # researcher topic tracking
    researchers_dispatched: list[str] = []

    try:
        async for mode, chunk in deep_researcher.astream(
            state_input,
            config=CONFIG,
            stream_mode=["values", "events"],
        ):

            # ── VALUES — state snapshots after each node ───────────────────
            if mode == "values":
                brief      = chunk.get("research_brief") or ""
                notes      = chunk.get("notes") or []
                profiles   = chunk.get("paper_profiles") or []
                sup_msgs   = chunk.get("supervisor_messages") or []
                critique   = chunk.get("critique_cycles", 0)
                report     = chunk.get("final_report", "")

                # education_discovery complete
                if brief and "discovery" not in seen_stages:
                    seen_stages.add("discovery")
                    subsection(f"[{ts()}] +{elapsed(start)}  NODE: education_discovery  COMPLETE")
                    print(f"  research_brief: {str(brief)[:300]}")

                # supervisor complete — extract researcher dispatches
                if len(sup_msgs) > prev_sup_msg_count and "supervisor" not in seen_stages:
                    seen_stages.add("supervisor")
                    prev_sup_msg_count = len(sup_msgs)
                    subsection(f"[{ts()}] +{elapsed(start)}  NODE: research_supervisor  COMPLETE")
                    print(f"  supervisor_messages: {len(sup_msgs)} messages")

                    # extract ConductResearch calls from AI message
                    for msg in sup_msgs:
                        tool_calls = []
                        if hasattr(msg, "tool_calls"):
                            tool_calls = msg.tool_calls or []
                        elif isinstance(msg, dict):
                            tool_calls = msg.get("tool_calls") or []
                            if not tool_calls:
                                tool_calls = (msg.get("additional_kwargs") or {}).get("tool_calls") or []

                        for tc in tool_calls:
                            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", "")
                            args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
                            if name == "ConductResearch":
                                topic = str(args.get("research_topic", ""))
                                kws   = args.get("keywords", [])
                                researchers_dispatched.append(topic)
                                print(f"  -> researcher #{len(researchers_dispatched)}: {topic[:120]}")
                                if kws:
                                    print(f"     keywords: {', '.join(str(k) for k in kws[:6])}")

                    if not researchers_dispatched:
                        print("  [!] could not parse ConductResearch calls — check message format")

                # researcher(s) returning notes
                if len(notes) > prev_note_count:
                    added = len(notes) - prev_note_count
                    prev_note_count = len(notes)
                    print(f"\n[{ts()}] +{elapsed(start)}  RESEARCHER DONE  notes: {len(notes)} total (+{added})", flush=True)
                    # print last note preview
                    for note in notes[-added:]:
                        preview = str(note)[:200].replace("\n", " ")
                        print(f"  note: {preview}...", flush=True)

                # paper profiles accumulating
                if len(profiles) > prev_paper_count:
                    prev_paper_count = len(profiles)
                    print(f"[{ts()}] +{elapsed(start)}  paper_profiles: {prev_paper_count} total", flush=True)

                # critique cycle
                if critique > 0 and f"critique_{critique}" not in seen_stages:
                    seen_stages.add(f"critique_{critique}")
                    subsection(f"[{ts()}] +{elapsed(start)}  NODE: supervisor_critique  cycle={critique}")

                # final report
                if report and "report" not in seen_stages:
                    seen_stages.add("report")
                    section(f"[{ts()}] +{elapsed(start)}  FINAL REPORT  ({len(report)} chars)")
                    print(report)

            # ── EVENTS — live tool/chain events ───────────────────────────
            elif mode == "events":
                event = chunk.get("event", "")
                name  = chunk.get("name", "")
                tags  = chunk.get("tags", [])

                if event == "on_tool_start" and name:
                    tool_call_counts[name] = tool_call_counts.get(name, 0) + 1
                    topic_tag = next((t for t in tags if t.startswith("researcher_topic:")), "")
                    topic_str = f"  [{topic_tag.replace('researcher_topic:', '')[:40]}]" if topic_tag else ""
                    print(f"[{ts()}]   TOOL  {name:<35} (×{tool_call_counts[name]}){topic_str}")

                elif event == "on_tool_end" and name:
                    out = chunk.get("data", {}).get("output", "") or ""
                    preview = str(out)[:80].replace("\n", " ")
                    print(f"[{ts()}]   DONE  {name:<35} -> {preview}")

                elif event == "on_chain_start" and name:
                    skip = {"LangGraph", "RunnableSequence", "RunnableLambda", ""}
                    if name not in skip and not name.startswith("__"):
                        print(f"[{ts()}]   NODE  {name}")

                elif event == "on_chain_error":
                    err = chunk.get("data", {}).get("error", "")
                    print(f"[{ts()}]   ERR   {name}: {err}")

    except Exception as e:
        section(f"PIPELINE EXCEPTION  [{ts()}]")
        print(f"  {type(e).__name__}: {e}")
        print(traceback.format_exc())

    # ── summary ────────────────────────────────────────────────────────────────
    section(f"RUN SUMMARY  [{ts()}]  total: +{elapsed(start)}")
    print(f"  researchers dispatched : {len(researchers_dispatched)}")
    for i, t in enumerate(researchers_dispatched, 1):
        print(f"    {i}. {t[:100]}")
    print()
    print(f"  tool calls:")
    for tool, count in sorted(tool_call_counts.items(), key=lambda x: -x[1]):
        print(f"    {tool:<40} {count}")
    print()
    print(f"  notes collected        : {prev_note_count}")
    print(f"  paper profiles         : {prev_paper_count}")
    hr("═")


if __name__ == "__main__":
    asyncio.run(run())

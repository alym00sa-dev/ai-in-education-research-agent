"""Main research pipeline graph — multi-iteration supervisor → synthesis → critique loop."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from configuration import Configuration
from nodes.education_discovery import education_discovery
from nodes.supervisor import supervisor_subgraph
from nodes.synthesis import compress_findings, draft_report
from nodes.critique import critique
from nodes.report import final_report
from nodes.qa import qa_audit
from state import AgentInputState, AgentState, SupervisorState


# ---------------------------------------------------------------------------
# Subgraph wrapper — maps AgentState ↔ SupervisorState
# ---------------------------------------------------------------------------

async def research_supervisor(state: AgentState, config: RunnableConfig) -> dict:
    """Run the supervisor subgraph and merge its outputs back into AgentState."""
    sub_input: SupervisorState = {
        "supervisor_messages": state.get("supervisor_messages", []),
        "research_brief": state.get("research_brief", ""),
        "tiered_question_map": state.get("tiered_question_map"),
        "notes": [],
        "raw_notes": [],
        "thought_log": [],
        "source_counts": {},
        "paper_profiles": [],
        "filtered_papers_log": [],
        "research_iterations": 0,
    }

    result = await supervisor_subgraph.ainvoke(sub_input, config)

    updates: dict = {}

    new_notes = result.get("notes") or []
    if new_notes:
        updates["notes"] = new_notes
        updates["all_notes"] = new_notes  # operator.add — accumulates across iterations
    new_raw = result.get("raw_notes") or []
    if new_raw:
        updates["raw_notes"] = new_raw
    if result.get("source_counts"):
        updates["source_counts"] = result["source_counts"]
    if result.get("paper_profiles"):
        updates["paper_profiles"] = result["paper_profiles"]
    if result.get("thought_log"):
        updates["thought_log"] = result["thought_log"]
    if result.get("filtered_papers_log"):
        updates["filtered_papers_log"] = result["filtered_papers_log"]

    return updates


# ---------------------------------------------------------------------------
# Iteration routing
# ---------------------------------------------------------------------------

def route_after_draft(state: AgentState, config: RunnableConfig) -> Literal["critique", "final_report_generation"]:
    """After drafting, go to critique if more iterations remain; else finalize."""
    configurable = Configuration.from_runnable_config(config)
    iteration = state.get("iteration", 0)
    # iterations=1 → no critique; iterations=N → N-1 critique cycles
    if iteration < configurable.research_iterations - 1:
        return "critique"
    return "final_report_generation"


# ---------------------------------------------------------------------------
# Build main graph
# ---------------------------------------------------------------------------

builder = StateGraph(AgentState, input=AgentInputState, config_schema=Configuration)

builder.add_node("education_discovery", education_discovery)
builder.add_node("research_supervisor", research_supervisor)
builder.add_node("compress_findings", compress_findings)
builder.add_node("draft_report", draft_report)
builder.add_node("critique", critique)
builder.add_node("final_report_generation", final_report)
builder.add_node("qa_audit", qa_audit)

builder.add_edge(START, "education_discovery")
# education_discovery uses Command(goto="research_supervisor") so no explicit edge needed
builder.add_edge("research_supervisor", "compress_findings")
builder.add_edge("compress_findings", "draft_report")
builder.add_conditional_edges(
    "draft_report",
    route_after_draft,
    {
        "critique": "critique",
        "final_report_generation": "final_report_generation",
    },
)
# After critique → back to supervisor for the next iteration
builder.add_edge("critique", "research_supervisor")
builder.add_edge("final_report_generation", "qa_audit")
builder.add_edge("qa_audit", END)

graph = builder.compile()

"""Synthesis nodes — compress_findings and draft_report."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import compress_findings_prompt, draft_report_prompt
from state import AgentState
from utils.llm import get_model, get_today_str


async def compress_findings(state: AgentState, config: RunnableConfig) -> dict:
    """Aggregate all researcher notes into a structured evidence summary."""
    notes = state.get("notes", [])
    model = get_model(config)

    prompt = compress_findings_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        n_researchers=len(notes),
    )
    findings_text = "\n\n---\n\n".join(notes) if notes else "No findings yet."

    response = await model.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content=findings_text),
    ])

    return {"compress_findings_history": [str(response.content)]}


async def draft_report(state: AgentState, config: RunnableConfig) -> dict:
    """Write a structured draft report from the current evidence summary."""
    configurable = Configuration.from_runnable_config(config)
    model = get_model(config)

    compress_history = state.get("compress_findings_history", [])
    current_compress = compress_history[-1] if compress_history else "No evidence summary available."
    iteration = state.get("iteration", 0)

    prompt = draft_report_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        iteration=iteration + 1,
        total_iterations=configurable.research_iterations,
        compress_findings=current_compress,
        max_sources=configurable.max_sources,
    )

    response = await model.ainvoke([HumanMessage(content=prompt)])
    return {"draft_report_history": [str(response.content)]}

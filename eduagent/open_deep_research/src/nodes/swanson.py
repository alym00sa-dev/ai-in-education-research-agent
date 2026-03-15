"""Swanson ABC node — novel hypothesis generation and causality diagram."""

import json
import re

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import swanson_abc_prompt
from state import AgentState
from utils.llm import configurable_model, get_api_key_for_model, get_today_str


def _extract_fenced_block(text: str, fence: str) -> str:
    """Extract content from a fenced block (e.g. ```json or ```mermaid)."""
    pattern = rf"```{fence}\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: return everything after the fence tag if closing fence missing
    pattern_open = rf"```{fence}\s*(.*)"
    match_open = re.search(pattern_open, text, re.DOTALL)
    if match_open:
        return match_open.group(1).strip()
    return ""


async def swanson_abc(state: AgentState, config: RunnableConfig) -> dict:
    """Run Swanson ABC analysis to surface novel hypotheses and generate causality diagram.

    Consumes ### MECHANISMS blocks from all sub-researcher compressed outputs.
    Produces:
    - swanson_hypotheses: list of novel A→C hypothesis dicts with citations + confidence
    - causality_diagram: Mermaid diagram string (injected into final report Section 2)
    """
    configurable = Configuration.from_runnable_config(config)
    model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"],
    }

    notes = state.get("notes", [])
    findings = "\n\n".join(notes) if notes else ""

    # If no mechanisms exist in the findings, skip gracefully
    if "### MECHANISMS" not in findings:
        return {
            "swanson_hypotheses": [],
            "causality_diagram": "```mermaid\ngraph LR\n```",
        }

    prompt = swanson_abc_prompt.format(
        date=get_today_str(),
        findings=findings,
    )

    try:
        response = await configurable_model.with_config(model_config).ainvoke([
            HumanMessage(content=prompt)
        ])
        raw = response.content or ""

        # Parse hypotheses JSON
        hypotheses = []
        if "### HYPOTHESES" in raw:
            hypotheses_section = raw.split("### HYPOTHESES", 1)[1]
            if "### CAUSALITY DIAGRAM" in hypotheses_section:
                hypotheses_section = hypotheses_section.split("### CAUSALITY DIAGRAM")[0]
            json_str = _extract_fenced_block(hypotheses_section, "json")
            if json_str:
                try:
                    hypotheses = json.loads(json_str)
                except json.JSONDecodeError:
                    hypotheses = []

        # Parse Mermaid diagram
        causality_diagram = "```mermaid\ngraph LR\n```"
        if "### CAUSALITY DIAGRAM" in raw:
            diagram_section = raw.split("### CAUSALITY DIAGRAM", 1)[1]
            mermaid_str = _extract_fenced_block(diagram_section, "mermaid")
            if mermaid_str:
                causality_diagram = f"```mermaid\n{mermaid_str}\n```"

        return {
            "swanson_hypotheses": hypotheses,
            "causality_diagram": causality_diagram,
        }

    except Exception as e:
        return {
            "swanson_hypotheses": [],
            "causality_diagram": f"_Causality diagram could not be generated: {e}_",
        }

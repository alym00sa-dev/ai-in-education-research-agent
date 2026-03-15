"""QA review node — coverage assessment and data extraction table generation."""

from langchain_core.messages import HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import qa_review_prompt
from state import AgentState
from utils.llm import configurable_model, get_api_key_for_model, get_today_str


async def qa_review(state: AgentState, config: RunnableConfig) -> dict:
    """Run a one-pass QA review before final report generation.

    Produces two outputs injected into the final report prompt:
    1. Coverage assessment — calibrates confidence for the report writer
    2. Data extraction table — pre-generated from sub-researcher findings
       using the user-defined column schema
    """
    configurable = Configuration.from_runnable_config(config)
    qa_model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"],
    }

    notes = state.get("notes", [])
    findings = "\n\n".join(notes) if notes else "No research findings available."

    # User context includes outline, keywords, and custom extraction schema
    # passed through clarification_answer in the message history
    user_context = get_buffer_string(state.get("messages", []))

    prompt = qa_review_prompt.format(
        date=get_today_str(),
        research_brief=state.get("research_brief", ""),
        user_context=user_context,
        findings=findings,
    )

    try:
        response = await configurable_model.with_config(qa_model_config).ainvoke([
            HumanMessage(content=prompt)
        ])
        raw = response.content or ""

        # Parse the two sections out of the response
        qa_assessment = ""
        extraction_table = ""

        if "### COVERAGE ASSESSMENT" in raw and "### DATA EXTRACTION TABLE" in raw:
            parts = raw.split("### DATA EXTRACTION TABLE", 1)
            qa_assessment = parts[0].replace("### COVERAGE ASSESSMENT", "").strip()
            extraction_table = parts[1].strip()
        elif "### COVERAGE ASSESSMENT" in raw:
            qa_assessment = raw.replace("### COVERAGE ASSESSMENT", "").strip()
        else:
            qa_assessment = raw.strip()

        return {
            "qa_assessment": qa_assessment,
            "extraction_table": extraction_table,
        }

    except Exception as e:
        return {
            "qa_assessment": f"QA review could not be completed: {e}",
            "extraction_table": "",
        }

"""Report generation node — synthesizes all research findings into a final report."""

from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig

from configuration import Configuration
from prompts import final_report_generation_prompt
from state import AgentState
from utils.llm import (
    configurable_model,
    get_api_key_for_model,
    get_model_token_limit,
    get_today_str,
    is_token_limit_exceeded,
)


async def final_report_generation(state: AgentState, config: RunnableConfig):
    """Generate the final comprehensive research report with retry logic for token limits.

    Takes all collected research findings and synthesizes them into a well-structured,
    comprehensive final report. Handles token limit errors with progressive truncation.

    Args:
        state: Agent state containing research findings and context
        config: Runtime configuration with model settings and API keys

    Returns:
        Dictionary containing the final report and cleared state
    """
    notes = state.get("notes", [])
    cleared_state = {}  # Notes preserved for audit trail and source log
    findings = "\n".join(notes)

    configurable = Configuration.from_runnable_config(config)
    writer_model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"]
    }

    # Build pre-scored tier lookup from paper_profiles extracted during research
    TIER_EMOJI = {"blue": "🔵", "green": "🟢", "yellow": "🟡", "red": "🔴"}
    profiles = state.get("paper_profiles", [])
    tier_lines = []
    for p in profiles:
        url = getattr(p, "url", None) or (p.get("url") if isinstance(p, dict) else None)
        quality = getattr(p, "quality_tier", None) or (p.get("quality_tier") if isinstance(p, dict) else None)
        impact = getattr(p, "impact_tier", None) or (p.get("impact_tier") if isinstance(p, dict) else None)
        title = getattr(p, "title", None) or (p.get("title") if isinstance(p, dict) else None)
        if url and quality and impact:
            q_emoji = TIER_EMOJI.get(str(quality).lower(), "🟡")
            i_emoji = TIER_EMOJI.get(str(impact).lower(), "🟡")
            label = f'"{title}" ' if title else ""
            tier_lines.append(f"- {label}{url} → Quality: {q_emoji} {quality} | Impact: {i_emoji} {impact}")
    paper_tier_reference = "\n".join(tier_lines) if tier_lines else "(No pre-scored profiles available — derive tiers from the rubric below.)"

    max_retries = 3
    current_retry = 0
    findings_token_limit = None

    while current_retry <= max_retries:
        try:
            final_report_prompt = final_report_generation_prompt.format(
                research_brief=state.get("research_brief", ""),
                messages=get_buffer_string(state.get("messages", [])),
                findings=findings,
                date=get_today_str(),
                paper_tier_reference=paper_tier_reference,
                max_sources=configurable.max_sources,
            )

            final_report = await configurable_model.with_config(writer_model_config).ainvoke([
                HumanMessage(content=final_report_prompt)
            ])

            return {
                "final_report": final_report.content,
                "messages": [final_report],
                **cleared_state
            }

        except Exception as e:
            if is_token_limit_exceeded(e, configurable.final_report_model):
                current_retry += 1

                if current_retry == 1:
                    model_token_limit = get_model_token_limit(configurable.final_report_model)
                    if not model_token_limit:
                        return {
                            "final_report": (
                                f"Error generating final report: Token limit exceeded, however, "
                                f"we could not determine the model's maximum context length. "
                                f"Please update MODEL_TOKEN_LIMITS in utils/llm.py. {e}"
                            ),
                            "messages": [AIMessage(content="Report generation failed due to token limits")],
                            **cleared_state
                        }
                    findings_token_limit = model_token_limit * 4
                else:
                    findings_token_limit = int(findings_token_limit * 0.9)

                findings = findings[:findings_token_limit]
                continue
            else:
                return {
                    "final_report": f"Error generating final report: {e}",
                    "messages": [AIMessage(content="Report generation failed due to an error")],
                    **cleared_state
                }

    return {
        "final_report": "Error generating final report: Maximum retries exceeded",
        "messages": [AIMessage(content="Report generation failed after maximum retries")],
        **cleared_state
    }

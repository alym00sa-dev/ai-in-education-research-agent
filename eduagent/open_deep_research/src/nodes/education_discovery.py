"""Education Discovery node — entry point for the research pipeline.

Transforms user messages into a structured research brief and initialises
the supervisor with system context. The supervisor itself handles research
decomposition using RST-style thinking and the 9 education dimensions as
a coverage guide.
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from configuration import Configuration
from prompts import lead_researcher_prompt, transform_messages_into_research_topic_prompt
from state import AgentState, ResearchQuestion
from utils.llm import configurable_model, get_api_key_for_model, get_today_str


async def education_discovery(
    state: AgentState,
    config: RunnableConfig,
) -> Command[Literal["research_supervisor"]]:
    """Transform user messages into a research brief and initialise supervisor context.

    Args:
        state: Current agent state containing user messages
        config: Runtime configuration with model settings

    Returns:
        Command to proceed to research supervisor with initialised context
    """
    configurable = Configuration.from_runnable_config(config)
    today = get_today_str()

    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }

    research_model = (
        configurable_model
        .with_structured_output(ResearchQuestion)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )

    messages = state.get("messages", [])
    prompt_content = transform_messages_into_research_topic_prompt.format(
        messages=get_buffer_string(messages),
        date=today,
    )
    response = await research_model.ainvoke([HumanMessage(content=prompt_content)])

    credit_budget = (
        f"**Shared Credit Budget (across ALL researchers and ALL iterations):**\n"
        f"- Tavily: {configurable.tavily_budget} calls total\n"
        f"- SerpAPI (Google Scholar): {configurable.serpapi_budget} calls total\n"
        f"- LLM web search (anthropic_web_search, openai_web_search): unlimited — use freely\n\n"
        f"**Allocation rules:**\n"
        f"- Do NOT use Tavily in iteration 1 — reserve it for iteration 2+ researchers targeting specific evidence gaps\n"
        f"- Allocate SerpAPI to 1–2 researchers with weakest DB coverage after iteration 1\n"
        f"- LLM web search is always available to all researchers at any iteration at no credit cost"
    )

    supervisor_system_prompt = lead_researcher_prompt.format(
        date=today,
        max_concurrent_research_units=configurable.max_concurrent_research_units,
        max_researcher_iterations=configurable.max_researcher_iterations,
        credit_budget=credit_budget,
    )

    return Command(
        goto="research_supervisor",
        update={
            "research_brief": response.research_brief,
            "supervisor_messages": {
                "type": "override",
                "value": [
                    SystemMessage(content=supervisor_system_prompt),
                    HumanMessage(content=response.research_brief),
                ]
            }
        }
    )

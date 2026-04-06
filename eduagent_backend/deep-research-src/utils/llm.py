"""LLM helpers, token management, and shared tools."""

import os
from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


def get_model(config: RunnableConfig = None):
    """Return an initialized chat model from the current configuration."""
    from configuration import Configuration
    configurable = Configuration.from_runnable_config(config)
    return init_chat_model(
        model=configurable.model,
        max_tokens=configurable.model_max_tokens,
    )


_JUDGE_MODEL = "anthropic:claude-opus-4-6"
_JUDGE_MAX_TOKENS = 4096


def get_judge_model():
    """Return the independent judge model (Claude claude-opus-4-6) used for QA scoring.

    Always uses a different provider than the pipeline model to avoid
    self-evaluation bias.
    """
    return init_chat_model(
        model=_JUDGE_MODEL,
        max_tokens=_JUDGE_MAX_TOKENS,
    )


def get_today_str() -> str:
    now = datetime.now()
    return f"{now:%a} {now:%b} {now.day}, {now:%Y}"


def get_api_key_for_model(model_name: str, config: RunnableConfig = None) -> str | None:
    """Get API key for a model from env or config."""
    should_get_from_config = os.getenv("GET_API_KEYS_FROM_CONFIG", "false")
    model_name = model_name.lower()
    if should_get_from_config.lower() == "true":
        api_keys = (config or {}).get("configurable", {}).get("apiKeys", {})
        if model_name.startswith("openai:"):
            return api_keys.get("OPENAI_API_KEY")
        elif model_name.startswith("anthropic:"):
            return api_keys.get("ANTHROPIC_API_KEY")
        return None
    else:
        if model_name.startswith("openai:"):
            return os.getenv("OPENAI_API_KEY")
        elif model_name.startswith("anthropic:"):
            return os.getenv("ANTHROPIC_API_KEY")
        return None


def is_token_limit_exceeded(exception: Exception, model_name: str = None) -> bool:
    """Check if an exception indicates a token/context limit was exceeded."""
    error_str = str(exception).lower()
    exception_type = str(type(exception))
    class_name = exception.__class__.__name__

    # OpenAI
    if "openai" in exception_type.lower():
        if class_name in ("BadRequestError", "InvalidRequestError"):
            if any(k in error_str for k in ("token", "context", "length", "maximum context", "reduce")):
                return True
        if hasattr(exception, "code") and getattr(exception, "code", "") == "context_length_exceeded":
            return True

    # Anthropic
    if "anthropic" in exception_type.lower():
        if class_name == "BadRequestError" and "prompt is too long" in error_str:
            return True

    return False


def remove_up_to_last_ai_message(messages: list) -> list:
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], AIMessage):
            return messages[:i]
    return messages


@tool(description="Strategic reflection tool for planning research approach")
def think_tool(reflection: str) -> str:
    """Use before dispatching researchers to reason through thread groupings, tier assignments,
    and keyword strategy. Write out your thinking — what threads to create, which tier, what
    the key questions are. Returns: confirmation that reflection was recorded."""
    return f"Reflection recorded: {reflection}"

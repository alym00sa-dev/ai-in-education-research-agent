"""
Environment configuration helper for Streamlit Cloud compatibility.
Supports both local .env files and Streamlit secrets.
"""
import os
from typing import Optional

# Try to import streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with Streamlit Cloud secrets fallback.

    Priority:
    1. Environment variable (os.environ)
    2. Streamlit secrets (st.secrets)
    3. Default value

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Value from environment, secrets, or default
    """
    # First try environment variable
    value = os.getenv(key)
    if value is not None:
        return value

    # Then try Streamlit secrets
    if HAS_STREAMLIT:
        try:
            value = st.secrets.get(key)
            if value is not None:
                # Set as environment variable for other code that uses os.getenv
                os.environ[key] = str(value)
                return str(value)
        except (FileNotFoundError, KeyError):
            pass

    # Return default
    return default


def load_env_config():
    """
    Load all required environment variables from Streamlit secrets if available.
    This allows existing code using os.getenv() to work with Streamlit Cloud.
    """
    if not HAS_STREAMLIT:
        return

    # List of all environment variables we need
    env_vars = [
        "NEO4J_URI",
        "NEO4J_USER",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
        "LANGGRAPH_API_URL",
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        "LANGSMITH_TRACING"
    ]

    # Load each from secrets to environment
    for var in env_vars:
        try:
            if var in st.secrets:
                os.environ[var] = str(st.secrets[var])
        except (FileNotFoundError, KeyError):
            pass

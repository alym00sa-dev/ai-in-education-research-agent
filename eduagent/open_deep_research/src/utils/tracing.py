"""Phoenix tracing setup — call setup_tracing() once at process startup.

Sends all LangChain/LangGraph spans to a local Phoenix server at localhost:6006.
Start Phoenix before running the app:
    pip install arize-phoenix
    python -m phoenix.server.main serve
    # or: phoenix serve
Then open http://localhost:6006 to view traces.
"""

import logging

logger = logging.getLogger(__name__)


def setup_tracing(project_name: str = "edu-deep-research") -> None:
    """Register Phoenix OTEL tracing and instrument LangChain globally.

    Safe to call multiple times — subsequent calls are no-ops if already registered.
    If Phoenix is not reachable, logs a warning and continues without tracing.

    Args:
        project_name: The project name shown in the Phoenix UI.
    """
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor

        tracer_provider = register(
            project_name=project_name,
            endpoint="http://localhost:6006/v1/traces",
            verbose=False,
        )
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        logger.info(f"[Phoenix] Tracing enabled — project '{project_name}' → http://localhost:6006")

    except ImportError:
        logger.warning("[Phoenix] arize-phoenix-otel or openinference-instrumentation-langchain not installed — tracing disabled.")
    except Exception as e:
        logger.warning(f"[Phoenix] Could not connect to Phoenix server — tracing disabled. ({e})")

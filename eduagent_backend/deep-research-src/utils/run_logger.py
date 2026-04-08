"""Per-session run logger — writes timestamped log lines to output/<session_id>/run.log.

Uses a global dict keyed by session_id so log calls from any node can find the
right file without relying on contextvars (which don't propagate across LangGraph
node task boundaries).

Falls back to print-only if no session is active (e.g. run_pipeline.py CLI).
"""

import os
import time

_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output")

# session_id -> (log_path, start_time)
_sessions: dict[str, tuple[str, float]] = {}


def init(session_id: str) -> None:
    """Initialize the run log for this session. Call once from education_discovery."""
    run_dir = os.path.join(_OUTPUT_DIR, session_id)
    os.makedirs(run_dir, exist_ok=True)
    path = os.path.join(run_dir, "run.log")
    start = time.time()
    _sessions[session_id] = (path, start)
    _write(path, start, "=" * 60)
    _write(path, start, "Deep Research — Frontend Run")
    _write(path, start, "=" * 60)


def _elapsed(start: float) -> str:
    e = int(time.time() - start)
    m, s = divmod(e, 60)
    return f"+{m}m{s:02d}s"


def _write(path: str, start: float, msg: str) -> None:
    try:
        with open(path, "a") as f:
            f.write(f"[{_elapsed(start)}] {msg}\n")
    except Exception:
        pass


def log(msg: str, session_id: str = "") -> None:
    """Write msg to stdout AND the session run.log (if session_id is known).
    Also dispatches a custom SSE event when running inside LangGraph Cloud."""
    print(msg, flush=True)
    if session_id and session_id in _sessions:
        path, start = _sessions[session_id]
        _write(path, start, msg)
    # Emit through the SSE stream when inside a LangGraph execution context
    try:
        from langchain_core.callbacks.manager import dispatch_custom_event
        dispatch_custom_event("log", {"message": msg})
    except Exception:
        pass


def total_elapsed_str(session_id: str) -> str:
    """Return human-readable total elapsed time for the session, e.g. '12m34s'."""
    if session_id and session_id in _sessions:
        _, start = _sessions[session_id]
        e = int(time.time() - start)
        m, s = divmod(e, 60)
        return f"{m}m{s:02d}s"
    return "unknown"

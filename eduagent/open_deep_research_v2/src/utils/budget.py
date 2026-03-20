"""Global per-run budget tracker for rate-limited search tools."""

import asyncio
import logging

logger = logging.getLogger(__name__)


class ToolBudget:
    """Thread-safe (asyncio) counter that enforces per-tool call limits for a run."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._counts: dict[str, int] = {}
        self._limits: dict[str, int] = {}

    def set_limit(self, tool_name: str, limit: int):
        self._limits[tool_name] = limit
        self._counts.setdefault(tool_name, 0)

    async def acquire(self, tool_name: str) -> bool:
        """Try to consume one credit for tool_name. Returns True if allowed."""
        limit = self._limits.get(tool_name)
        if limit is None:
            return True  # no limit set — always allow
        async with self._lock:
            current = self._counts.get(tool_name, 0)
            if current >= limit:
                logger.info(f"[budget] {tool_name} budget exhausted ({current}/{limit}) — skipping")
                return False
            self._counts[tool_name] = current + 1
            return True

    def usage(self) -> dict[str, str]:
        return {k: f"{self._counts.get(k, 0)}/{self._limits.get(k, '∞')}" for k in self._limits}


# Module-level singleton — reset at the start of each pipeline run
_budget = ToolBudget()


def get_budget() -> ToolBudget:
    return _budget


def reset_budget(tavily_limit: int = 10, serp_limit: int = 3):
    """Call once at the start of each run to reset counters."""
    global _budget
    _budget = ToolBudget()
    _budget.set_limit("tavily_search", tavily_limit)
    _budget.set_limit("scholar_search", serp_limit)
    logger.info(f"[budget] Reset — tavily={tavily_limit}, scholar_search={serp_limit}")

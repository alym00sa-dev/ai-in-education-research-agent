"""SyncResearchPipeline — synchronous wrapper for use in Streamlit."""
import asyncio
import queue
import threading
from typing import Any, Dict, Generator, List, Optional

from src.pipeline.orchestrator import ResearchPipeline
from src.pipeline.langgraph_client import StreamEvent, stream_open_deep_research


class SyncResearchPipeline:
    """Synchronous wrapper around the async ResearchPipeline."""

    def __init__(self):
        self.pipeline = ResearchPipeline()

    def _run(self, coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    # ── Fast helpers ──────────────────────────────────────────────────────────

    def get_clarification(self, query: str, model_provider: str) -> Dict[str, Any]:
        return self._run(self.pipeline.get_clarification(query=query, model_provider=model_provider))

    def get_report_structure(self, query: str, context: str, model_provider: str) -> str:
        return self._run(self.pipeline.get_report_structure(
            query=query, context=context, model_provider=model_provider,
        ))

    # ── Batch research (kept for session-history loading) ─────────────────────

    def conduct_research(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        focus_area: str = "all",
        clarification_answer: Optional[str] = None,
        skip_clarification: bool = False,
        _prefetched_summary: Optional[str] = None,
        _prefetched_sources: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        return self._run(self.pipeline.conduct_research(
            query=query, model_provider=model_provider, search_depth=search_depth,
            focus_area=focus_area, clarification_answer=clarification_answer,
            skip_clarification=skip_clarification,
            _prefetched_summary=_prefetched_summary, _prefetched_sources=_prefetched_sources,
        ))

    # ── Streaming research ────────────────────────────────────────────────────

    def stream_research(
        self,
        query: str,
        model_provider: str = "openai:gpt-4.1",
        search_depth: str = "standard",
        clarification_answer: Optional[str] = None,
        skip_clarification: bool = False,
        max_sources: int = 20,
    ) -> Generator[StreamEvent, None, None]:
        """Synchronous generator that yields StreamEvent dicts in real time.

        Runs the async streaming generator in a background thread and bridges
        events back to the calling (Streamlit) thread via a queue.

        Yields StreamEvent dicts with type in:
          node_start | node_end | token | result | error | done
        """
        langgraph_url = self.pipeline.langgraph_url
        event_queue: queue.Queue = queue.Queue()
        _SENTINEL = object()

        def run_in_thread():
            async def _drain():
                try:
                    async for event in stream_open_deep_research(
                        query=query,
                        model_provider=model_provider,
                        search_depth=search_depth,
                        langgraph_url=langgraph_url,
                        clarification_answer=clarification_answer,
                        skip_clarification=skip_clarification,
                        max_sources=max_sources,
                    ):
                        event_queue.put(event)
                except Exception as exc:
                    event_queue.put(StreamEvent(
                        type="error", node="", content=str(exc), metadata={},
                    ))
                finally:
                    event_queue.put(_SENTINEL)

            asyncio.run(_drain())

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

        while True:
            item = event_queue.get()
            if item is _SENTINEL:
                break
            yield item

        thread.join()

    def finalize_streamed_research(
        self,
        session,
        research_summary: str,
        sources: List[Dict],
        audit_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Run post-processing (extract, persist, return) after streaming completes."""
        return self._run(self.pipeline.finalize_streamed_research(
            session=session,
            research_summary=research_summary,
            sources=sources,
            audit_data=audit_data,
        ))

    def create_session(self, query: str, model_provider: str, search_depth: str, focus_area: str = "all"):
        return self.pipeline.create_session(
            query=query, model_provider=model_provider,
            search_depth=search_depth, focus_area=focus_area,
        )

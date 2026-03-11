"""LangGraph HTTP client — non-streaming and streaming calls."""
import json
import os
import re
from typing import Any, AsyncGenerator, Dict, List, Optional
from typing_extensions import TypedDict, Literal

import httpx


# ── Event schema ──────────────────────────────────────────────────────────────

class StreamEvent(TypedDict):
    type: str       # "node_start" | "node_end" | "token" | "result" | "error" | "done"
    node: str       # node/graph name, empty string if not applicable
    content: str    # human-readable text or token chunk
    metadata: dict  # raw event payload for the audit trail


# ── Human-readable node labels ─────────────────────────────────────────────────

_NODE_LABELS = {
    "write_research_brief":    "Writing research brief",
    "research_supervisor":     "Research supervisor",
    "supervisor":              "Supervisor planning",
    "supervisor_tools":        "Dispatching sub-researchers",
    "final_report_generation": "Generating final report",
    "clarify_with_user":       "Clarifying query",
}

_IGNORED_NODES = {"__start__", "__end__", "LangGraph"}


def _iterations_for_depth(search_depth: str) -> int:
    return {"standard": 4, "deep": 6, "comprehensive": 8}.get(search_depth, 4)


def _build_payload(
    query: str,
    model_provider: str,
    search_depth: str,
    clarification_answer: Optional[str],
    skip_clarification: bool,
    stream_mode,
) -> tuple[str, dict]:
    """Return (content_str, payload_dict)."""
    content = (
        f"{query}\n\nAdditional context from the user: {clarification_answer}"
        if clarification_answer
        else query
    )
    configurable: Dict[str, Any] = {
        "research_model": model_provider,
        "max_researcher_iterations": _iterations_for_depth(search_depth),
    }
    if skip_clarification or clarification_answer:
        configurable["allow_clarification"] = False

    payload = {
        "assistant_id": "Deep Researcher",
        "input": {"messages": [{"role": "user", "content": content}]},
        "config": {"configurable": configurable},
        "stream_mode": stream_mode,
    }
    return content, payload


# ── Non-streaming call (used for background/batch path) ───────────────────────

async def call_open_deep_research(
    query: str,
    model_provider: str,
    search_depth: str,
    langgraph_url: str,
    clarification_answer: Optional[str] = None,
    skip_clarification: bool = False,
) -> Dict[str, Any]:
    """Run the LangGraph deep-research graph and return the final result dict."""
    _, payload = _build_payload(
        query, model_provider, search_depth,
        clarification_answer, skip_clarification,
        stream_mode="values",
    )

    async with httpx.AsyncClient(timeout=600.0) as client:
        thread_resp = await client.post(f"{langgraph_url}/threads", json={})
        thread_resp.raise_for_status()
        thread_id = thread_resp.json()["thread_id"]

        response = await client.post(
            f"{langgraph_url}/threads/{thread_id}/runs/stream",
            json=payload,
        )
        response.raise_for_status()

        final_state = None
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str == "[DONE]":
                    continue
                try:
                    data = json.loads(data_str)
                    if data:
                        final_state = data
                except json.JSONDecodeError:
                    continue

    if not final_state:
        raise RuntimeError("No response from LangGraph server")

    return _parse_final_state(final_state)


# ── Streaming call (yields StreamEvents for live UI) ──────────────────────────

async def stream_open_deep_research(
    query: str,
    model_provider: str,
    search_depth: str,
    langgraph_url: str,
    clarification_answer: Optional[str] = None,
    skip_clarification: bool = False,
) -> AsyncGenerator[StreamEvent, None]:
    """Stream LangGraph events as StreamEvent dicts.

    Yields node_start / node_end / token events during the run, then a final
    'result' event containing the parsed research output for downstream use.
    """
    _, payload = _build_payload(
        query, model_provider, search_depth,
        clarification_answer, skip_clarification,
        stream_mode=["values", "events"],
    )

    async with httpx.AsyncClient(timeout=600.0) as client:
        thread_resp = await client.post(f"{langgraph_url}/threads", json={})
        thread_resp.raise_for_status()
        thread_id = thread_resp.json()["thread_id"]

        final_state: Optional[dict] = None
        current_event_type: Optional[str] = None

        async with client.stream(
            "POST",
            f"{langgraph_url}/threads/{thread_id}/runs/stream",
            json=payload,
        ) as response:
            response.raise_for_status()

            async for raw_line in response.aiter_lines():
                raw_line = raw_line.strip()
                if not raw_line:
                    continue

                # Track SSE event type (e.g. "event: events" or "event: values")
                if raw_line.startswith("event: "):
                    current_event_type = raw_line[7:].strip()
                    continue

                if not raw_line.startswith("data: "):
                    continue

                data_str = raw_line[6:]
                if data_str == "[DONE]":
                    continue

                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if not data:
                    continue

                # ── values stream → keep as latest full state ──────────────
                if current_event_type == "values":
                    final_state = data
                    continue

                # ── events stream → yield UI events ───────────────────────
                if current_event_type != "events":
                    continue

                event_name = data.get("event", "")
                node_name = data.get("name", "")
                tags = data.get("tags", [])

                if node_name in _IGNORED_NODES:
                    continue

                # ── Section boundaries ──────────────────────────────────────
                if event_name == "on_chain_start":
                    if node_name == "write_research_brief":
                        yield StreamEvent(type="section_start", node=node_name, content="system", metadata={})
                    elif node_name == "final_report_generation":
                        yield StreamEvent(type="section_start", node=node_name, content="final", metadata={})
                    elif node_name == "supervisor_tools":
                        # Extract ConductResearch topics from the pending supervisor tool calls
                        try:
                            sup_messages = data.get("data", {}).get("input", {}).get("supervisor_messages", [])
                            for msg in sup_messages:
                                tc_list = msg.get("tool_calls", []) if isinstance(msg, dict) else []
                                for tc in tc_list if isinstance(tc_list, list) else []:
                                    if isinstance(tc, dict) and tc.get("name") == "ConductResearch":
                                        topic = (tc.get("args") or {}).get("research_topic", "")
                                        if topic:
                                            yield StreamEvent(type="sub_researcher_start", node="ConductResearch", content=topic, metadata={})
                        except Exception:
                            pass

                elif event_name == "on_chain_end":
                    if node_name == "final_report_generation":
                        yield StreamEvent(type="section_end", node=node_name, content="final", metadata={})
                    elif node_name == "compress_research":
                        # A sub-researcher has finished
                        yield StreamEvent(type="sub_researcher_done", node="compress_research", content="", metadata={})

                # ── Thoughts from think_tool (supervisor + researchers) ─────
                elif event_name == "on_tool_start" and node_name == "think_tool":
                    reflection = (data.get("data", {}).get("input") or {}).get("reflection", "")
                    if reflection:
                        yield StreamEvent(type="thought", node="think_tool", content=reflection, metadata={})

                # ── Token streaming (respects langsmith:nostream tag) ───────
                elif event_name == "on_chat_model_stream" and "langsmith:nostream" not in tags:
                    chunk = data.get("data", {}).get("chunk", {})
                    token = ""
                    if isinstance(chunk, dict):
                        content_val = chunk.get("content", "")
                        if isinstance(content_val, str):
                            token = content_val
                        elif isinstance(content_val, list):
                            token = "".join(
                                c.get("text", "") for c in content_val
                                if isinstance(c, dict)
                            )
                    if token:
                        yield StreamEvent(type="token", node=node_name, content=token, metadata={})

    if not final_state:
        yield StreamEvent(type="error", node="", content="No response from LangGraph server", metadata={})
        return

    result = _parse_final_state(final_state)
    yield StreamEvent(type="result", node="", content="", metadata=result)
    yield StreamEvent(type="done", node="", content="", metadata={})


# ── Shared state parsing ───────────────────────────────────────────────────────

def _parse_final_state(state: dict) -> Dict[str, Any]:
    """Extract final report + sources from a LangGraph values-stream state snapshot."""
    final_report = state.get("final_report_generation", {}).get("final_report", "")
    if not final_report:
        final_report = state.get("final_report", "")

    # Fallback: last AI message
    if not final_report:
        for msg in reversed(state.get("messages", [])):
            role = msg.get("type", "") or msg.get("role", "")
            if role in ("ai", "assistant"):
                content = msg.get("content", "")
                if isinstance(content, list):
                    final_report = " ".join(
                        c.get("text", "") for c in content if isinstance(c, dict)
                    )
                else:
                    final_report = content
                break

    sources = _extract_sources(final_report, state)
    return {"summary": final_report, "sources": sources}


def _extract_sources(report: str, state: dict) -> List[Dict[str, str]]:
    sources = []

    supervisor_node = state.get("research_supervisor", {})
    raw_notes = supervisor_node.get("raw_notes", []) or state.get("raw_notes", [])

    for note in raw_notes:
        if isinstance(note, str):
            for url in re.findall(r"https?://[^\s\)\"'\]>]+", note):
                sources.append({"url": url, "title": url.split("/")[-1]})

    for url in re.findall(r"https?://[^\s\)\"'\]>]+", report):
        if not any(s["url"] == url for s in sources):
            sources.append({"url": url, "title": url.split("/")[-1]})

    seen: set = set()
    unique = []
    for s in sources:
        if s["url"] not in seen:
            seen.add(s["url"])
            unique.append(s)
    return unique[:18]

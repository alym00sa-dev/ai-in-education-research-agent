"""Pydantic models for Session API responses."""
from pydantic import BaseModel
from typing import Optional


class SessionResponse(BaseModel):
    """Basic session information."""
    session_id: str
    query: str
    created_at: str
    model_provider: str
    search_depth: str
    focus_area: str
    paper_count: int
    follow_up_count: int
    status: str


class SessionDetail(SessionResponse):
    """Detailed session information including research report."""
    research_report: str = ""


class GraphResponse(BaseModel):
    """Graph visualization data for a session."""
    session_id: str
    graph: dict  # { nodes: [...], edges: [...] }
    stats: dict  # { node_count, edge_count }

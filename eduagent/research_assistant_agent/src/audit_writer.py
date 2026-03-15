"""Session audit writer — persists full research audit trail to sessions/{session_id}.json."""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


_SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sessions")


def write_session_audit(
    session_id: str,
    query: str,
    research_summary: str,
    sources: List[Dict],
    structured_papers: Optional[List[Dict]] = None,
    audit_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Write the full session audit trail to sessions/{session_id}.json.

    Args:
        session_id: Unique session identifier.
        query: Original user query.
        research_summary: Final report markdown.
        sources: List of source dicts (url, title).
        structured_papers: Extracted paper metadata (from KG extractor).
        audit_data: Raw metadata from _parse_final_state, containing:
            qa_assessment, extraction_table, swanson_hypotheses,
            causality_diagram, notes.

    Returns:
        Absolute path to the written file.
    """
    os.makedirs(_SESSIONS_DIR, exist_ok=True)
    audit_data = audit_data or {}

    payload = {
        "session_id": session_id,
        "query": query,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "final_report": research_summary,
        "qa_assessment": audit_data.get("qa_assessment"),
        "extraction_table": audit_data.get("extraction_table"),
        "swanson_hypotheses": audit_data.get("swanson_hypotheses"),
        "causality_diagram": audit_data.get("causality_diagram"),
        "sub_researcher_notes": audit_data.get("notes", []),
        "sources": sources,
        "structured_papers": structured_papers or [],
    }

    path = os.path.join(_SESSIONS_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

    return path


def load_session_audit(session_id: str) -> Dict[str, Any]:
    """Load a previously written session audit file.

    Returns the parsed dict, or an empty dict if the file doesn't exist
    (e.g. sessions created before audit writing was implemented).
    """
    path = os.path.join(_SESSIONS_DIR, f"{session_id}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

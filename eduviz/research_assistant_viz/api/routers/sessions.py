"""Session API endpoints."""
from fastapi import APIRouter, HTTPException
from api.models.session import SessionResponse, SessionDetail, GraphResponse
from api.services.session_service import SessionService

router = APIRouter()
service = SessionService()


@router.get("", response_model=dict)
async def list_sessions(limit: int = 50):
    """List all research sessions, most recent first.

    Args:
        limit: Maximum number of sessions to return (default: 50)

    Returns:
        Dictionary with 'sessions' list and 'total' count
    """
    try:
        sessions = service.list_sessions(limit)
        return {
            "sessions": [s.to_dict() for s in sessions],
            "total": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    """Get detailed information for a specific session.

    Args:
        session_id: UUID of the session

    Returns:
        SessionDetail with full session information
    """
    try:
        session = service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@router.get("/{session_id}/papers")
async def get_session_papers(session_id: str):
    """Get all papers from a specific session.

    Args:
        session_id: UUID of the session

    Returns:
        Dictionary with session_id, paper_count, and papers list
    """
    try:
        papers = service.get_session_papers(session_id)
        return {
            "session_id": session_id,
            "paper_count": len(papers),
            "papers": papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session papers: {str(e)}")


@router.get("/{session_id}/graph", response_model=GraphResponse)
async def get_session_graph(session_id: str):
    """Get graph visualization data for a session.

    Args:
        session_id: UUID of the session

    Returns:
        GraphResponse with nodes, edges, and statistics
    """
    try:
        graph_data = service.get_session_graph(session_id)
        return {
            "session_id": session_id,
            "graph": graph_data,
            "stats": {
                "node_count": len(graph_data.get('nodes', [])),
                "edge_count": len(graph_data.get('edges', []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session graph: {str(e)}")

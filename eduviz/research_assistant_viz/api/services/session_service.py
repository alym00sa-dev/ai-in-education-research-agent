"""Service layer for session operations."""
from typing import List, Dict, Any, Optional
from src.session_manager import SessionManager, ResearchSession


class SessionService:
    """Service layer wrapping session manager operations."""

    def __init__(self):
        """Initialize session service with SessionManager."""
        self.manager = SessionManager()

    def list_sessions(self, limit: int = 50) -> List[ResearchSession]:
        """List all research sessions, most recent first.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of ResearchSession objects
        """
        return self.manager.list_sessions(limit)

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Get specific session by ID.

        Args:
            session_id: UUID of the session

        Returns:
            ResearchSession object or None if not found
        """
        return self.manager.get_session(session_id)

    def get_session_papers(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all papers from a specific session.

        Args:
            session_id: UUID of the session

        Returns:
            List of paper dictionaries with full metadata
        """
        return self.manager.get_session_papers(session_id)

    def get_session_graph(self, session_id: str) -> Dict[str, Any]:
        """Get graph visualization data for session.

        Args:
            session_id: UUID of the session

        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        return self.manager.get_session_graph(session_id)

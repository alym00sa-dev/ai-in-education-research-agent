"""Service layer for evidence map operations."""
from typing import List, Dict, Any
import pandas as pd
from src.evidence_map import (
    create_full_matrix,
    get_paper_details_for_cell,
    get_cached_synthesis,
    synthesize_papers_for_cell
)


class EvidenceMapService:
    """Service layer wrapping evidence map queries."""

    def get_matrix(self) -> pd.DataFrame:
        """Get full evidence map matrix with all 48 cells.

        Returns:
            DataFrame with implementation_objective, outcome, count columns
        """
        return create_full_matrix()

    def get_cell_papers(self, io: str, outcome: str) -> List[Dict[str, Any]]:
        """Get papers for specific Implementation Objective × Outcome cell.

        Args:
            io: Implementation Objective
            outcome: Outcome focus area

        Returns:
            List of paper dictionaries with all metadata
        """
        return get_paper_details_for_cell(io, outcome)

    def get_cell_synthesis(
        self,
        io: str,
        outcome: str,
        force_regenerate: bool = False
    ) -> Dict[str, str]:
        """Get or generate AI synthesis for a specific cell.

        Args:
            io: Implementation Objective
            outcome: Outcome focus area
            force_regenerate: If True, regenerate even if cached

        Returns:
            Dictionary with 'overview', 'gaps', 'generated_at' keys
        """
        # Check cache first unless force regenerate
        if not force_regenerate:
            cached = get_cached_synthesis(io, outcome)
            if cached:
                return cached

        # Generate new synthesis
        papers = self.get_cell_papers(io, outcome)
        return synthesize_papers_for_cell(io, outcome, papers, force_regenerate)

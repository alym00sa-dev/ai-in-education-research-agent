"""Evidence Map API endpoints."""
from fastapi import APIRouter, HTTPException
from api.models.evidence_map import MatrixResponse, EvidenceCellResponse, SynthesisResponse
from api.services.evidence_map_service import EvidenceMapService

router = APIRouter()
service = EvidenceMapService()


@router.get("/matrix", response_model=MatrixResponse)
async def get_matrix():
    """Get full evidence map matrix with all 48 cells (4 IO × 12 Outcomes).

    Returns:
        MatrixResponse with cells and totals
    """
    try:
        df = service.get_matrix()
        cells = df.to_dict('records')
        totals = {
            "total_papers": int(df['count'].sum()),
            "cells_with_data": int((df['count'] > 0).sum())
        }
        return {"cells": cells, "totals": totals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evidence matrix: {str(e)}")


@router.get("/cell/{io}/{outcome}", response_model=EvidenceCellResponse)
async def get_cell(io: str, outcome: str):
    """Get papers for a specific Implementation Objective × Outcome cell.

    Args:
        io: Implementation Objective (URL-encoded)
        outcome: Outcome (URL-encoded)

    Returns:
        EvidenceCellResponse with papers and metadata
    """
    try:
        papers = service.get_cell_papers(io, outcome)
        return {
            "implementation_objective": io,
            "outcome": outcome,
            "paper_count": len(papers),
            "papers": papers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cell papers: {str(e)}")


@router.get("/cell/{io}/{outcome}/synthesis", response_model=SynthesisResponse)
async def get_synthesis(io: str, outcome: str, force_regenerate: bool = False):
    """Get or generate AI synthesis for a specific cell.

    Args:
        io: Implementation Objective (URL-encoded)
        outcome: Outcome (URL-encoded)
        force_regenerate: If True, regenerate even if cached (default: False)

    Returns:
        SynthesisResponse with overview and gaps
    """
    try:
        synthesis = service.get_cell_synthesis(io, outcome, force_regenerate)
        papers = service.get_cell_papers(io, outcome)
        return {
            "implementation_objective": io,
            "outcome": outcome,
            "synthesis": synthesis,
            "paper_count": len(papers),
            "from_cache": not force_regenerate and synthesis is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve/generate synthesis: {str(e)}")

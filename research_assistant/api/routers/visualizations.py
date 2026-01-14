"""API routes for visualization data."""

from fastapi import APIRouter, HTTPException
from api.models.visualization import Level1Response, Level2Response
from api.services.visualization_service import VisualizationService

router = APIRouter()
service = VisualizationService()


@router.get("/level1", response_model=Level1Response)
async def get_level1_visualization():
    """
    Get data for Level 1: Problem Burden Map.
    Returns 12 bubbles (one per outcome).
    """
    try:
        data = service.get_level1_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level2", response_model=Level2Response)
async def get_level2_visualization():
    """
    Get data for Level 2: Intervention Evidence Map.
    Returns 4 bubbles (one per Implementation Objective).
    """
    try:
        data = service.get_level2_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

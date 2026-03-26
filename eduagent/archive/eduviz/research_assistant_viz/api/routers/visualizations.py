"""API routes for visualization data."""

from fastapi import APIRouter, HTTPException
from api.models.visualization import Level1Response, Level2Response, Level5Response, P5Response, P1Response, P1CurrentResponse, P1CurrentByCaseResponse
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


@router.get("/level3", response_model=Level2Response)
async def get_level3_visualization():
    """
    Get data for Level 3: Evidence-Based Interventions Map (WWC).
    Returns 4 bubbles (one per Implementation Objective) with RCT evidence.
    """
    try:
        data = service.get_level3_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level4", response_model=Level2Response)
async def get_level4_visualization():
    """
    Get data for Level 4: Individual Interventions (WWC).
    Returns 67 bubbles (one per tech-compatible intervention).
    """
    try:
        data = service.get_level4_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level5", response_model=Level5Response)
async def get_level5_visualization():
    """
    Get data for Level 5: Evidence Evolution Over Time (WWC).
    Returns time series showing how interventions scaled from 1995-2025.
    """
    try:
        data = service.get_level5_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/p5", response_model=P5Response)
async def get_p5_visualization():
    """
    Get data for P5: Delivery Pillar (Adaptive Instruction & Tutoring).
    Returns geographic, demographic, institution, and grade level distributions over time.
    """
    try:
        data = service.get_p5_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/p1", response_model=P1Response)
async def get_p1_visualization():
    """
    Get data for P1: Effect Size Evolution Over Time.
    Returns time series of effect sizes for 20 adaptive instruction interventions.
    Two views: by intervention (20 lines) and by use_case (5 lines).
    """
    try:
        data = service.get_p1_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gates-investment-overlap")
async def get_gates_investment_overlap():
    """
    Get data for Gates Investment Pre-LLM Overlap visualization.
    Returns state-level data showing overlap between Gates Foundation investments
    and WWC study concentration for Core Instruction & Tutoring.
    """
    try:
        data = service.get_gates_investment_overlap_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/p1-current/{implementation_objective}", response_model=P1CurrentResponse)
async def get_p1_current_visualization(implementation_objective: str):
    """
    Get data for P1Current: Evidence Ladder visualization.
    Returns non-WWC papers classified into 6 evidence ladder rungs.

    Args:
        implementation_objective: The implementation objective to filter by
    """
    try:
        data = service.get_p1_current_data(implementation_objective)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/p1-current-by-usecase/{implementation_objective}", response_model=P1CurrentByCaseResponse)
async def get_p1_current_by_usecase_visualization(implementation_objective: str):
    """
    Get data for P1Current by Use Case: Evidence Ladders grouped by use case.
    Returns 5 evidence ladders (one per use case: math_tutoring, automated_grading,
    real_time_feedback, instructional_planning, teacher_coaching).

    Args:
        implementation_objective: The implementation objective to filter by
    """
    try:
        data = service.get_p1_current_by_usecase(implementation_objective)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

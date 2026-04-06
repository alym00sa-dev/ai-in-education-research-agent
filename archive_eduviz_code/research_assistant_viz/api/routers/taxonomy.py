"""Taxonomy API endpoints (read-only controlled vocabularies)."""
from fastapi import APIRouter
from src.neo4j_config import (
    IMPLEMENTATION_OBJECTIVES,
    OUTCOMES,
    POPULATIONS,
    USER_TYPES,
    STUDY_DESIGNS
)

router = APIRouter()


@router.get("/implementation-objectives")
async def get_implementation_objectives():
    """Get list of all Implementation Objectives.

    Returns:
        Dictionary with 'items' list
    """
    return {"items": IMPLEMENTATION_OBJECTIVES}


@router.get("/outcomes")
async def get_outcomes():
    """Get list of all Outcomes (cognitive, behavioral, affective).

    Returns:
        Dictionary with 'items' list
    """
    return {"items": OUTCOMES}


@router.get("/populations")
async def get_populations():
    """Get list of all study populations (Elementary, High School, etc.).

    Returns:
        Dictionary with 'items' list
    """
    return {"items": POPULATIONS}


@router.get("/user-types")
async def get_user_types():
    """Get list of all user types (Student, Educator, etc.).

    Returns:
        Dictionary with 'items' list
    """
    return {"items": USER_TYPES}


@router.get("/study-designs")
async def get_study_designs():
    """Get list of all study designs (RCT, Quasi-Experimental, etc.).

    Returns:
        Dictionary with 'items' list
    """
    return {"items": STUDY_DESIGNS}

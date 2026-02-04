"""Pydantic models for Evidence Map API responses."""
from pydantic import BaseModel
from typing import List, Optional


class PaperResponse(BaseModel):
    """Individual paper with all metadata."""
    title: str
    url: str
    year: Optional[int] = None
    venue: Optional[str] = None
    population: Optional[str] = None
    user_type: Optional[str] = None
    study_design: Optional[str] = None
    finding_direction: Optional[str] = None
    results_summary: Optional[str] = None
    measure: Optional[str] = None
    study_size: Optional[int] = None
    effect_size: Optional[float] = None


class EvidenceCellResponse(BaseModel):
    """Response for a specific Implementation Objective × Outcome cell."""
    implementation_objective: str
    outcome: str
    paper_count: int
    papers: List[PaperResponse]


class MatrixCell(BaseModel):
    """Single cell in the evidence matrix."""
    implementation_objective: str
    outcome: str
    count: int


class MatrixResponse(BaseModel):
    """Full evidence map matrix with all 48 cells."""
    cells: List[MatrixCell]
    totals: dict  # { total_papers, cells_with_data }


class SynthesisResponse(BaseModel):
    """AI-generated synthesis for a specific cell."""
    implementation_objective: str
    outcome: str
    synthesis: dict  # { overview, gaps, generated_at }
    paper_count: int
    from_cache: bool

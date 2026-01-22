"""Pydantic models for visualization endpoints."""

from pydantic import BaseModel
from typing import List, Optional, Dict


class BubbleData(BaseModel):
    """Single bubble in visualization."""
    id: str
    label: str
    x: float  # Evidence maturity (0-100)
    y: float  # Problem burden scale OR potential impact
    size: float  # Bubble size (investment/effort)
    color: Optional[str] = None
    priority: str  # Priority tag: high_priority, on_watch, research_gap
    paper_count: int

    # Breakdown data for click interaction
    breakdown: Dict


class Level1Response(BaseModel):
    """Response for Level 1: Problem Burden Map."""
    bubbles: List[BubbleData]
    metadata: Dict  # Legend info, axis descriptions


class Level2Response(BaseModel):
    """Response for Level 2: Intervention Evidence Map."""
    bubbles: List[BubbleData]
    metadata: Dict  # Legend info, axis descriptions, investment amounts


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    period: str
    year_midpoint: float
    implementation_reach: float
    cumulative_students: int
    num_contexts: int
    avg_effect_size: float
    num_studies: int
    new_students_this_period: int


class TimeSeriesData(BaseModel):
    """Time series for one Implementation Objective."""
    id: str
    label: str
    color: str
    data_points: List[TimeSeriesDataPoint]


class Level5Response(BaseModel):
    """Response for Level 5: Evidence Evolution Over Time."""
    time_series: List[TimeSeriesData]
    metadata: Dict  # Axis descriptions

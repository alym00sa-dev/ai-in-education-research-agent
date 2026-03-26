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


class ContextsData(BaseModel):
    """Context diversity data for a time period."""
    regions: List[str]
    school_types: List[str]
    populations: List[str]


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    period: str
    year_midpoint: float
    generalizability_score: float
    cumulative_students: int
    new_students_this_period: int
    avg_effect_size: float
    num_studies: int
    contexts: ContextsData


class TimeSeriesData(BaseModel):
    """Time series for one Implementation Objective."""
    id: str
    label: str
    color: str
    data_points: List[TimeSeriesDataPoint]
    first_year: Optional[int] = None


class Level5Response(BaseModel):
    """Response for Level 5: Evidence Evolution Over Time."""
    time_series: List[TimeSeriesData]
    individual_interventions: Dict[str, List[TimeSeriesData]]
    metadata: Dict  # Axis descriptions


class P5GeographicDataPoint(BaseModel):
    """Geographic data point for a state."""
    state: str
    student_count: int
    study_count: int
    interventions: Optional[Dict[str, int]] = None  # intervention_name -> student_count


class P5DemographicDataPoint(BaseModel):
    """Demographic distribution data point by state."""
    state: str
    category: str  # FRPL, ELL, IEP, Minority
    student_count: int
    percentage: float


class P5InstitutionDataPoint(BaseModel):
    """Institution type distribution data point by state."""
    state: str
    institution_type: str  # Public, Charter, Private, Parochial
    count: int
    percentage: float


class P5GradeLevelDataPoint(BaseModel):
    """Grade level distribution data point by state."""
    state: str
    grade_level: str  # Early Childhood (PK), Elementary (K-5), Middle (6-8), High School (9-12)
    student_count: int
    percentage: float


class P5TimeSlice(BaseModel):
    """Data for a single time period."""
    year: int
    geographic_data: List[P5GeographicDataPoint]
    demographic_data: List[P5DemographicDataPoint]
    institution_data: List[P5InstitutionDataPoint]
    grade_level_data: List[P5GradeLevelDataPoint]
    total_students: int
    total_studies: int


class P5Response(BaseModel):
    """Response for P5: Delivery Pillar (Adaptive Instruction & Tutoring)."""
    time_slices: List[P5TimeSlice]  # Data grouped by year for time slider
    all_years: List[int]  # Available years for slider
    metadata: Dict  # Descriptions and scaling info


# P1: Effect Size Over Time Models

class P1Finding(BaseModel):
    """Single finding within a study."""
    effect_size: float
    outcome_measure: str
    outcome_domain: str  # Domain category (e.g., Alphabetics, Phonology)
    period: str  # Timing of measurement (e.g., immediate, 1 Year follow-up)
    sample_description: str  # Sample or subgroup details
    is_subgroup: bool  # Whether this is a subgroup analysis
    intervention_mean: Optional[float]  # Intervention group mean score
    comparison_mean: Optional[float]  # Control/comparison group mean score
    comparison_clusters: Optional[int]  # Number of schools/sites in control group (for cluster RCTs)
    is_significant: bool
    direction: str  # Favorable, Unfavorable, No discernable effect size direction


class P1Study(BaseModel):
    """Study details for a data point."""
    study_id: str
    citation: str
    sample_size: int
    intervention_name: Optional[str] = None  # Intervention name (for use-case view)
    findings: List[P1Finding]


class P1DataPoint(BaseModel):
    """Single year data point in effect size time series."""
    year: int
    effect_size: float  # Average effect size for this year
    new_students: int  # New students studied this year
    cumulative_students: int  # Total students up to this year
    num_findings: int  # Number of findings this year
    num_studies: int  # Number of unique studies this year
    dominant_direction: str  # Favorable, Unfavorable, or No discernable effect size direction
    studies: List[P1Study]  # Details of all studies for this year


class P1Series(BaseModel):
    """Time series for one intervention or use case."""
    id: str
    label: str
    color: str
    use_case: Optional[str] = None  # Only for intervention series
    data_points: List[P1DataPoint]


class P1Response(BaseModel):
    """Response for P1: Effect Size Evolution Over Time."""
    intervention_series: List[P1Series]  # 20 lines (one per intervention)
    usecase_series: List[P1Series]  # 5 lines (one per use case)
    metadata: Dict  # Axis descriptions and bubble color meanings


# P1Current: Evidence Ladder Models

class P1CurrentPaper(BaseModel):
    """Individual paper details for evidence ladder."""
    title: str
    url: Optional[str] = None
    year: Optional[int] = None
    study_design: Optional[str] = None
    population: Optional[str] = None
    outcomes: List[str] = []


class P1CurrentRung(BaseModel):
    """Data for a single evidence ladder rung."""
    rung_number: int
    rung_name: str
    description: str
    paper_count: int
    papers: List[P1CurrentPaper]


class P1CurrentResponse(BaseModel):
    """Response for P1Current: Evidence Ladder Visualization."""
    rungs: List[P1CurrentRung]  # 6 rungs from Monitoring to Personalized
    total_papers: int
    implementation_objective: str
    metadata: Dict  # Descriptions and classifications


class P1CurrentUseCaseLadder(BaseModel):
    """Evidence ladder for a single use case."""
    use_case_id: str
    use_case_label: str
    rungs: List[P1CurrentRung]


class P1CurrentByCaseResponse(BaseModel):
    """Response for P1Current by Use Case: Evidence Ladders by Use Case."""
    use_case_ladders: List[P1CurrentUseCaseLadder]  # 5 use cases, each with 6 rungs
    total_papers: int
    implementation_objective: str
    metadata: Dict  # Descriptions and use case list

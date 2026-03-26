"""Graph state definitions and data structures for the Deep Research agent."""

import operator
from typing import Annotated, Optional

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict


###################
# KG-Aligned Paper Profile
###################

OUTCOME_OPTIONS = [
    "Academic — Literacy",
    "Academic — Language Fluency",
    "Academic — Mathematical Numeracy",
    "Academic — Scientific Reasoning",
    "Academic — Other",
    "Social-Emotional Skills",
    "Durable Skills",
    "Operational Efficiency",
    "Systemic / Institutional Impact",
]

STUDY_DESIGN_OPTIONS = [
    "Randomized Controlled Trial (RCT)",
    "Quasi-Experimental Design (QED)",
    "Meta-Analysis / Systematic Review",
    "Observational / Correlational",
    "Mixed-Methods",
    "Qualitative",
]

OUTCOME_CONFIDENCE_THRESHOLD = 0.7


class EmpiricalFindingExtract(BaseModel):
    """Empirical finding aligned to KG EmpiricalFinding node schema."""

    direction: str = Field(
        description="One of: Positive, Negative, No Effect, Mixed"
    )
    finding_summary: str = Field(
        description=(
            "2-3 sentence summary of this specific finding. "
            "Include effect sizes (e.g. d=0.42), sample sizes (n=), and outcome measures where reported."
        )
    )
    measure: str = Field(
        default="not_reported",
        description="What was measured (e.g. standardized test scores, engagement surveys)",
    )
    study_size: str = Field(
        default="not_reported",
        description="Sample size (e.g. n=312) or 'not_reported'",
    )
    effect_size: str = Field(
        default="not_reported",
        description="Effect size value (e.g. d=0.42, g=0.31) or 'not_reported'",
    )
    confidence_interval: str = Field(
        default="not_reported",
        description="95% CI or 'not_reported'",
    )
    std_deviation: str = Field(
        default="not_reported",
        description="Standard deviation or 'not_reported'",
    )


class OutcomeAssignment(BaseModel):
    """One outcome area this paper substantively focuses on, with confidence score and finding."""

    outcome: str = Field(
        description=f"One of the 9 outcome categories: {', '.join(OUTCOME_OPTIONS)}"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How substantively this paper focuses on this outcome (0.0–1.0). "
            "Only include outcomes the paper directly studies, not tangential mentions. "
            "Only return assignments with confidence ≥ 0.5."
        ),
    )
    finding: EmpiricalFindingExtract = Field(
        description="The empirical finding for this outcome area."
    )


class PaperProfile(BaseModel):
    """Full KG-aligned paper profile produced during PDF extraction."""

    # Core metadata — maps directly to Paper node properties
    title: str
    doi: Optional[str] = None
    year: Optional[int] = None

    @field_validator("year", mode="before")
    @classmethod
    def coerce_year(cls, v: object) -> Optional[int]:
        if v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None
    venue: Optional[str] = None
    url: str = ""
    source_db: str = ""
    population: str = Field(
        default="not_reported",
        description="Target population (e.g. Elementary (PreK-5th), High School, Undergraduate, Adult)",
    )
    user_type: str = Field(
        default="not_reported",
        description="One of: Student, Educator, Administrator, Parent, School, Community",
    )
    study_design: str = Field(
        default="not_reported",
        description=f"One of: {', '.join(STUDY_DESIGN_OPTIONS)}",
    )
    extended_summary: str = Field(
        default="",
        description=(
            "Abstract plus 2-3 paragraph gist covering the study's purpose, "
            "approach, context, and main conclusions. Enough to understand the paper without reading it."
        ),
    )

    # K-12 Evidence Framework tiers — scored at extraction time from full paper text
    # Quality: research design + credibility + relevance
    # Impact: effect size + priority population focus
    # Values: "blue" | "green" | "yellow" | "red"
    quality_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Quality tier: blue, green, yellow, or red",
    )
    impact_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Impact tier: blue, green, yellow, or red",
    )

    # Outcome assignments — LLM returns outcomes it finds relevant (confidence ≥ 0.5)
    # Code filters to OUTCOME_CONFIDENCE_THRESHOLD (0.7) before writing to KG
    outcome_assignments: list[OutcomeAssignment] = Field(default_factory=list)

    # Extraction metadata
    extraction_status: str = Field(
        default="abstract_only",
        description="'full_text' or 'abstract_only'",
    )
    extraction_note: str = Field(
        default="",
        description="Reason if abstract_only (e.g. 'paywall (HTTP 403)', 'timeout')",
    )


###################
# Structured Outputs
###################
class ConductResearch(BaseModel):
    """Call this tool to dispatch a researcher to answer a focused sub-question."""
    research_topic: str = Field(
        description="A focused research sub-question (1-2 sentences). Should be a specific, answerable question — not a broad topic description.",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="3-5 search keywords or quoted phrases to guide database queries (e.g. '\"high-dosage tutoring\" effect size K-8').",
    )

class ResearchComplete(BaseModel):
    """Call this tool to indicate that the research is complete."""

class Summary(BaseModel):
    """Research summary with key findings."""
    
    summary: str
    key_excerpts: str

class ClarifyWithUser(BaseModel):
    """Model for user clarification requests."""
    
    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )

class ResearchQuestion(BaseModel):
    """Research question and brief for guiding research."""

    research_brief: str = Field(
        description="A research question that will be used to guide the research.",
    )


###################
# State Definitions
###################

def override_reducer(current_value, new_value):
    """Reducer function that allows overriding values in state."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    else:
        return operator.add(current_value, new_value)


def merge_source_counts(current: dict, new: dict) -> dict:
    """Merge source count dicts by summing values per tool."""
    result = dict(current)
    for k, v in new.items():
        result[k] = result.get(k, 0) + v
    return result
    
class AgentInputState(MessagesState):
    """InputState is only 'messages'."""

class AgentState(MessagesState):
    """Main agent state containing messages and research data."""

    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: Optional[str]
    raw_notes: Annotated[list[str], override_reducer] = []
    notes: Annotated[list[str], override_reducer] = []
    final_report: str
    qa_assessment: Optional[str] = None
    extraction_table: Optional[str] = None
    swanson_hypotheses: Optional[list] = None
    causality_diagram: Optional[str] = None
    thought_log: Annotated[list[dict], operator.add]
    source_counts: Annotated[dict, merge_source_counts]
    paper_profiles: Annotated[list[PaperProfile], operator.add]
    critique_cycles: int = 0

class SupervisorState(TypedDict):
    """State for the supervisor that manages research tasks."""

    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: str
    notes: Annotated[list[str], override_reducer] = []
    research_iterations: int = 0
    raw_notes: Annotated[list[str], override_reducer] = []
    thought_log: Annotated[list[dict], operator.add]
    source_counts: Annotated[dict, merge_source_counts]
    paper_profiles: Annotated[list[PaperProfile], operator.add]

class ResearcherState(TypedDict):
    """State for individual researchers conducting research."""

    researcher_messages: Annotated[list[MessageLikeRepresentation], operator.add]
    tool_call_iterations: int = 0
    sweep_cycles: int = 0
    web_search_calls: int = 0
    source_counts: Annotated[dict, merge_source_counts]
    thought_log: Annotated[list[dict], operator.add]
    filtered_papers_log: Annotated[list[dict], operator.add]
    paper_profiles: Annotated[list[PaperProfile], operator.add]
    keyword_history: Annotated[list[dict], operator.add]
    current_keyword_set: Optional[dict]
    research_topic: str
    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []

class ResearcherOutputState(BaseModel):
    """Output state from individual researchers."""

    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []
    thought_log: list = []
    source_counts: dict = {}
    filtered_papers_log: list = []
    paper_profiles: list = []
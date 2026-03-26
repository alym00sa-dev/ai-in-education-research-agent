"""Graph state definitions and data structures for the Deep Research v2 agent."""

import operator
from typing import Annotated, Literal, Optional

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
            "How substantively this paper focuses on this outcome (0.0-1.0). "
            "Only include outcomes the paper directly studies, not tangential mentions. "
            "Only return assignments with confidence >= 0.5."
        ),
    )
    finding: EmpiricalFindingExtract = Field(
        description="The empirical finding for this outcome area."
    )


class PaperProfile(BaseModel):
    """Full KG-aligned paper profile produced during PDF extraction."""

    # Core metadata
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

    # K-12 Evidence Framework tiers
    quality_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Quality tier: blue, green, yellow, or red",
    )
    impact_tier: str = Field(
        default="yellow",
        description="K-12 Evidence Framework Impact tier: blue, green, yellow, or red",
    )

    # Outcome assignments
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
# Reducers
###################

def override_reducer(current, new):
    """Reducer that allows overriding values via tagged dict."""
    if isinstance(new, dict) and new.get("type") == "override":
        return new.get("value", new)
    return operator.add(current, new)


def merge_source_counts(current: dict, new: dict) -> dict:
    """Merge source count dicts by summing values per tool."""
    result = dict(current)
    for k, v in new.items():
        result[k] = result.get(k, 0) + v
    return result


###################
# State Definitions
###################

class AgentInputState(MessagesState):
    """Input state — only messages."""
    pass


class AgentState(MessagesState):
    """Main agent state."""

    research_brief: str = ""
    tiered_question_map: Optional[dict] = None
    supervisor_messages: Annotated[list, override_reducer] = []
    iteration: int = 0
    executive_summary_history: Annotated[list[str], operator.add] = []
    critique_history: Annotated[list[str], operator.add] = []
    notes: Annotated[list[str], override_reducer] = []
    raw_notes: Annotated[list[str], override_reducer] = []
    all_notes: Annotated[list[str], operator.add] = []  # accumulates across all iterations
    final_report: str = ""
    qa_report: str = ""
    qa_score: int = 0
    paper_profiles: Annotated[list[PaperProfile], operator.add] = []
    source_counts: Annotated[dict, merge_source_counts] = {}
    thought_log: Annotated[list[dict], operator.add] = []
    filtered_papers_log: Annotated[list[dict], operator.add] = []


class SupervisorState(TypedDict):
    """State for the supervisor subgraph."""

    supervisor_messages: Annotated[list, override_reducer]
    research_brief: str
    tiered_question_map: Optional[dict]
    notes: Annotated[list[str], override_reducer]
    raw_notes: Annotated[list[str], override_reducer]
    thought_log: Annotated[list[dict], operator.add]
    source_counts: Annotated[dict, merge_source_counts]
    paper_profiles: Annotated[list[PaperProfile], operator.add]
    filtered_papers_log: Annotated[list[dict], operator.add]
    research_iterations: int


class ResearcherState(TypedDict):
    """State for individual researcher agents."""

    researcher_messages: Annotated[list, operator.add]
    sweep_cycles: int
    web_search_calls: int
    source_counts: Annotated[dict, merge_source_counts]
    thought_log: Annotated[list[dict], operator.add]
    filtered_papers_log: Annotated[list[dict], operator.add]
    paper_profiles: Annotated[list[PaperProfile], operator.add]
    keyword_history: Annotated[list[dict], operator.add]
    current_keyword_set: Optional[dict]
    research_topic: str
    tier: str
    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer]


class ResearcherOutputState(BaseModel):
    """Output state from individual researcher agents."""

    compressed_research: str
    raw_notes: list = []
    thought_log: list = []
    source_counts: dict = {}
    filtered_papers_log: list = []
    paper_profiles: list = []


###################
# Structured Output Models
###################

class ResearchBrief(BaseModel):
    """Parsed output from education_discovery — research brief + 4-tier question map."""
    topic: str
    focal_intervention: str
    population: str
    context: str
    target_skills_outcomes: str
    likely_comparators: str
    key_research_priority: str
    tier1: list[str] = Field(description="Foundational framing questions")
    tier2: list[str] = Field(description="Baseline and existing approaches questions")
    tier3: list[str] = Field(description="Mechanisms and implementation questions")
    tier4: list[str] = Field(description="Comparative evidence and implications questions")


class ConductResearch(BaseModel):
    research_topic: str = Field(description="A research thread — 1-3 related questions to investigate together")
    keywords: list[str] = Field(description="3-5 search keywords for DB queries")
    tier: str = Field(description="Primary tier: 'tier1', 'tier2', 'tier3', or 'tier4'")


class ResearchComplete(BaseModel):
    pass


class KeywordSet(BaseModel):
    primary_query: str
    variation_query: str
    web_query: str


class ReflectionDecision(BaseModel):
    decision: Literal["PASS", "NEEDS_WORK"]
    gaps: list[str] = []
    new_primary_query: str = ""
    new_variation_query: str = ""
    new_web_query: str = ""


class CritiqueOutput(BaseModel):
    evidence_gaps: list[str]
    thesis_gaps: list[str]
    missing_angles: list[str]
    next_iteration_brief: str


class QAScores(BaseModel):
    """Structured scores-only output from the QA audit — kept small for reliable tool use."""
    citation_score: int = Field(ge=0, le=20, description="Citation-bibliography linkage score (0-20)")
    statistic_score: int = Field(ge=0, le=25, description="Statistic provenance score (0-25)")
    study_design_score: int = Field(ge=0, le=15, description="Study design accuracy score (0-15)")
    coverage_score: int = Field(ge=0, le=20, description="Sub-question coverage score (0-20)")
    url_score: int = Field(ge=0, le=20, description="URL integrity score (0-20)")

    @property
    def overall_score(self) -> int:
        return self.citation_score + self.statistic_score + self.study_design_score + self.coverage_score + self.url_score

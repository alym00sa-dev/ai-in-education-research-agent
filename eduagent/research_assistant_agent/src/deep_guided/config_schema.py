"""Data models for Deep Guided mode."""
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ResearchGoal:
    goal_id: str
    statement: str

    @classmethod
    def new(cls, statement: str) -> "ResearchGoal":
        return cls(goal_id=str(uuid.uuid4())[:8], statement=statement)


@dataclass
class TechConfig:
    research_model: str = "openai:gpt-4.1"
    search_depth: str = "deep"
    evidence_hierarchy: List[str] = field(default_factory=lambda: [
        "Randomized Controlled Trial (RCT)",
        "Quasi-experimental",
        "Longitudinal",
        "Cross-sectional",
        "Case study",
        "Literature review / meta-analysis",
    ])
    source_domains: List[str] = field(default_factory=lambda: [
        "Academic databases",
        "Government reports",
        "Think tank reports",
        "Grey literature",
    ])
    citation_scoring: Dict[str, int] = field(default_factory=lambda: {
        "recency": 7,
        "study_design": 9,
        "sample_size": 6,
        "effect_size": 8,
    })


@dataclass
class Codebook:
    scoring_rubric: str = ""
    # keyed by goal_id
    research_directions: Dict[str, str] = field(default_factory=dict)


@dataclass
class SupplementaryStudy:
    filename: str
    text: str
    annotation: str = ""


@dataclass
class DeepGuidedSession:
    chat_history: List[Dict[str, str]] = field(default_factory=list)
    goals: List[ResearchGoal] = field(default_factory=list)
    tech_config: TechConfig = field(default_factory=TechConfig)
    codebook: Codebook = field(default_factory=Codebook)
    supplementary_studies: List[SupplementaryStudy] = field(default_factory=list)
    results: Optional[Dict[str, Any]] = None

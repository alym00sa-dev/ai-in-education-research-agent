"""Parallel multi-goal research runner.

This module will run each approved ResearchGoal through the deep research
pipeline concurrently, using one thread+queue bridge per goal (same pattern
as SyncResearchPipeline.stream_research), then merge results into a unified
session. Currently a stub — the interface is defined and ready to wire up.
"""
from typing import List, Dict, Any, Generator

from src.deep_guided.config_schema import ResearchGoal, TechConfig, Codebook, SupplementaryStudy


def build_goal_query(
    goal: ResearchGoal,
    codebook: Codebook,
    supplementary_studies: List[SupplementaryStudy],
) -> str:
    """Compose the full query string for one goal, injecting codebook + study context."""
    parts = [goal.statement]

    directions = codebook.research_directions.get(goal.goal_id, "")
    if directions:
        parts.append(f"\n\nResearch directions:\n{directions}")

    if codebook.scoring_rubric:
        parts.append(f"\n\nScoring rubric for evidence evaluation:\n{codebook.scoring_rubric}")

    if supplementary_studies:
        study_lines = [
            f"- {s.filename}: {s.annotation}"
            for s in supplementary_studies
            if s.annotation
        ]
        if study_lines:
            parts.append(f"\n\nSupplementary studies to consider:\n" + "\n".join(study_lines))

    return "".join(parts)


def run_goals_parallel(
    goals: List[ResearchGoal],
    tech_config: TechConfig,
    codebook: Codebook,
    supplementary_studies: List[SupplementaryStudy],
    langgraph_url: str,
) -> Generator[Dict[str, Any], None, None]:
    """
    Stream events for all goals in parallel, each tagged with goal_id.

    Implementation plan:
    - One thread+queue bridge per goal (same pattern as SyncResearchPipeline.stream_research)
    - Main loop polls all queues in round-robin and yields events tagged {"goal_id": ..., **event}
    - Finalization runs after all goals complete: per-goal results merged into one unified report

    TODO: implement when parallel streaming UI is ready.
    """
    raise NotImplementedError(
        "Parallel multi-goal runner not yet implemented. "
        "Wire to stream_open_deep_research with one thread+queue bridge per goal."
    )

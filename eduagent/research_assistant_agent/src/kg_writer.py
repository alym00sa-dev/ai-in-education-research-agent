"""KG writer — writes PaperProfile objects directly to Neo4j.

Replaces the LLM extraction step in kg_extractor.py for newly discovered papers.
PaperProfiles are already fully structured by the pdf_extractor pipeline.

Only full_text profiles are written to the KG; abstract_only profiles are skipped.
"""
from datetime import datetime
from typing import Any, List

from src.neo4j_config import get_neo4j_connection

# Mirror of the threshold in open_deep_research/src/state.py
OUTCOME_CONFIDENCE_THRESHOLD = 0.7


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Get a field from either a Pydantic model or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class KGWriter:
    """Writes PaperProfile objects to the Neo4j knowledge graph."""

    def __init__(self):
        self.conn = get_neo4j_connection()

    def write_paper_profiles(self, profiles: List[Any], session_id: str) -> int:
        """Write a list of PaperProfile objects to Neo4j.

        Only writes profiles with extraction_status == "full_text".

        Args:
            profiles: List of PaperProfile objects (Pydantic) or equivalent dicts.
            session_id: Session ID to tag papers with.

        Returns:
            Number of papers successfully written.
        """
        added_count = 0
        added_date = datetime.now().isoformat()

        with self.conn.driver.session(database=self.conn.database) as db_session:
            for profile in profiles:
                if _get(profile, "extraction_status") != "full_text":
                    continue
                try:
                    self._write_one(db_session, profile, session_id, added_date)
                    added_count += 1
                except Exception as e:
                    title = _get(profile, "title", "Unknown")
                    print(f"  ❌ Failed to write {str(title)[:60]}: {e}")

        return added_count

    def _write_one(self, db_session, profile: Any, session_id: str, added_date: str):
        title = _get(profile, "title", "Unknown")

        doi = _get(profile, "doi")
        if doi and str(doi).strip().lower() in ("not_reported", ""):
            doi = None

        paper_params = {
            "title": title,
            "doi": doi,
            "year": _get(profile, "year"),
            "venue": _get(profile, "venue") or "",
            "url": _get(profile, "url") or "",
            "source_db": _get(profile, "source_db") or "",
            "population": _get(profile, "population") or "",
            "user_type": _get(profile, "user_type") or "",
            "study_design": _get(profile, "study_design") or "",
            "extended_summary": _get(profile, "extended_summary") or "",
            "extraction_status": _get(profile, "extraction_status") or "full_text",
            "quality_tier": _get(profile, "quality_tier") or "",
            "impact_tier": _get(profile, "impact_tier") or "",
            "session_id": session_id,
            "added_date": added_date,
        }

        # MERGE Paper — DOI-first deduplication, fallback to title
        if doi:
            db_session.run(
                """
                MERGE (p:Paper {doi: $doi})
                ON CREATE SET
                    p.title = $title, p.year = $year, p.venue = $venue,
                    p.url = $url, p.source_db = $source_db,
                    p.population = $population, p.user_type = $user_type,
                    p.study_design = $study_design,
                    p.extended_summary = $extended_summary,
                    p.extraction_status = $extraction_status,
                    p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                    p.session_id = $session_id, p.added_date = $added_date
                ON MATCH SET
                    p.title = $title, p.source_db = $source_db,
                    p.population = $population, p.user_type = $user_type,
                    p.study_design = $study_design,
                    p.extended_summary = $extended_summary,
                    p.extraction_status = $extraction_status,
                    p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                    p.session_id = $session_id
                """,
                paper_params,
            )
        else:
            db_session.run(
                """
                MERGE (p:Paper {title: $title})
                ON CREATE SET
                    p.year = $year, p.venue = $venue,
                    p.url = $url, p.source_db = $source_db,
                    p.population = $population, p.user_type = $user_type,
                    p.study_design = $study_design,
                    p.extended_summary = $extended_summary,
                    p.extraction_status = $extraction_status,
                    p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                    p.session_id = $session_id, p.added_date = $added_date
                ON MATCH SET
                    p.source_db = $source_db,
                    p.population = $population, p.user_type = $user_type,
                    p.study_design = $study_design,
                    p.extended_summary = $extended_summary,
                    p.extraction_status = $extraction_status,
                    p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                    p.session_id = $session_id
                """,
                paper_params,
            )

        # Write outcome assignments
        outcome_assignments = _get(profile, "outcome_assignments") or []
        for assignment in outcome_assignments:
            confidence = _get(assignment, "confidence", 0.0)
            if confidence < OUTCOME_CONFIDENCE_THRESHOLD:
                continue

            outcome_name = _get(assignment, "outcome", "")
            if not outcome_name:
                continue

            finding = _get(assignment, "finding")
            if finding is None:
                continue

            # Stable finding_id scoped to paper + outcome
            finding_id = f"finding_{abs(hash(str(title) + outcome_name)) % 10_000_000}"

            # MERGE relationship with confidence score
            db_session.run(
                """
                MATCH (p:Paper {title: $title})
                MATCH (out:Outcome {name: $outcome_name})
                MERGE (p)-[r:FOCUSES_ON_OUTCOME]->(out)
                SET r.confidence = $confidence
                """,
                {"title": title, "outcome_name": outcome_name, "confidence": confidence},
            )

            # MERGE EmpiricalFinding and link to paper
            db_session.run(
                """
                MATCH (p:Paper {title: $title})
                MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                ON CREATE SET
                    f.direction = $direction,
                    f.finding_summary = $finding_summary,
                    f.measure = $measure,
                    f.study_size = $study_size,
                    f.effect_size = $effect_size,
                    f.confidence_interval = $confidence_interval,
                    f.std_deviation = $std_deviation
                MERGE (p)-[:REPORTS_FINDING]->(f)
                """,
                {
                    "title": title,
                    "finding_id": finding_id,
                    "direction": _get(finding, "direction", ""),
                    "finding_summary": _get(finding, "finding_summary", ""),
                    "measure": _get(finding, "measure", "not_reported"),
                    "study_size": _get(finding, "study_size", "not_reported"),
                    "effect_size": _get(finding, "effect_size", "not_reported"),
                    "confidence_interval": _get(finding, "confidence_interval", "not_reported"),
                    "std_deviation": _get(finding, "std_deviation", "not_reported"),
                },
            )

            # Link finding to outcome
            db_session.run(
                """
                MATCH (out:Outcome {name: $outcome_name})
                MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                MERGE (out)-[:HAS_FINDING]->(f)
                """,
                {"outcome_name": outcome_name, "finding_id": finding_id},
            )

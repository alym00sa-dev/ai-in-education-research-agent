"""KG writer — persists PaperProfile objects to Neo4j after a pipeline run.

Only writes profiles with extraction_status == "full_text".
Reads connection details from env: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE.
"""
import logging
import os
from datetime import datetime
from typing import Any

log = logging.getLogger(__name__)

OUTCOME_CONFIDENCE_THRESHOLD = 0.7

# Interventions that are AI-powered (used when seeding Intervention nodes)
_AI_POWERED = {
    "Intelligent Tutoring System (ITS)",
    "LLM-based Tutoring / Conversational AI",
    "Adaptive Learning Platform",
    "Automated Feedback System",
    "AI Writing / Language Tool",
    "Robot / Embodied Tutor",
    "Predictive Analytics / Early Warning",
}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Get a field from a Pydantic model or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _slug(name: str) -> str:
    """Convert a canonical name to a slug id."""
    import re
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def write_paper_profiles(profiles: list[Any], session_id: str) -> int:
    """Write full_text PaperProfile objects to Neo4j.

    Args:
        profiles: PaperProfile objects (Pydantic or dict).
        session_id: Run identifier — tags each paper node.

    Returns:
        Number of papers successfully written.
    """
    full_text = [p for p in profiles if _get(p, "extraction_status") == "full_text"]
    if not full_text:
        log.info("[kg_writer] No full_text profiles — skipping KG write.")
        return 0

    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
    except Exception as e:
        log.error(f"[kg_writer] Neo4j connection failed — skipping: {e}")
        return 0

    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    added_date = datetime.now().isoformat()
    count = 0

    with driver.session(database=database) as db:
        for profile in full_text:
            try:
                _write_one(db, profile, session_id, added_date)
                count += 1
            except Exception as e:
                title = _get(profile, "title", "Unknown")
                log.error(f"[kg_writer] Failed '{str(title)[:60]}': {e}")

    driver.close()
    log.info(f"[kg_writer] Wrote {count}/{len(full_text)} profiles to Neo4j (session={session_id}).")
    return count


def _write_one(db_session, profile: Any, session_id: str, added_date: str):
    title = _get(profile, "title", "Unknown")
    doi = _get(profile, "doi")
    if doi and str(doi).strip().lower() in ("not_reported", ""):
        doi = None

    # ── Paper node ────────────────────────────────────────────────────────────
    params = {
        "title": title,
        "doi": doi,
        "year": _get(profile, "year"),
        "venue": _get(profile, "venue") or "",
        "url": _get(profile, "url") or "",
        "source_db": _get(profile, "source_db") or "",
        "populations": _get(profile, "populations") or [],
        "user_types": _get(profile, "user_types") or [],
        "study_design": _get(profile, "study_design") or "not_reported",
        "extended_summary": _get(profile, "extended_summary") or "",
        "extraction_status": _get(profile, "extraction_status") or "full_text",
        "quality_tier": _get(profile, "quality_tier") or "",
        "impact_tier": _get(profile, "impact_tier") or "",
        "session_id": session_id,
        "added_date": added_date,
        # New fields
        "limitations": _get(profile, "limitations") or [],
        "duration_weeks": _get(profile, "duration_weeks") or "not_reported",
        "setting": _get(profile, "setting") or "not_reported",
        "teacher_training": _get(profile, "teacher_training") or "not_reported",
        "implementation_fidelity": _get(profile, "implementation_fidelity") or "not_reported",
        "study_country": _get(profile, "study_country") or "not_reported",
        "study_region": _get(profile, "study_region") or "not_reported",
    }

    if doi:
        db_session.run(
            """
            MERGE (p:Paper {doi: $doi})
            ON CREATE SET
                p.title = $title, p.year = $year, p.venue = $venue,
                p.url = $url, p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.extraction_status = $extraction_status,
                p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.session_id = $session_id, p.added_date = $added_date
            ON MATCH SET
                p.title = $title, p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.extraction_status = $extraction_status,
                p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.session_id = $session_id
            """,
            params,
        )
    else:
        db_session.run(
            """
            MERGE (p:Paper {title: $title})
            ON CREATE SET
                p.year = $year, p.venue = $venue,
                p.url = $url, p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.extraction_status = $extraction_status,
                p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.session_id = $session_id, p.added_date = $added_date
            ON MATCH SET
                p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.extraction_status = $extraction_status,
                p.quality_tier = $quality_tier, p.impact_tier = $impact_tier,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.session_id = $session_id
            """,
            params,
        )

    # ── Tool nodes (IdentifiedTool) + EVALUATES relationships ────────────────
    identified_tools = _get(profile, "identified_tools") or []
    primary_intervention_id = None

    for tool in identified_tools:
        tool_name = _get(tool, "name", "")
        if not tool_name:
            continue
        use_case = _get(tool, "use_case", "")
        is_named = _get(tool, "is_named_product", False)
        is_ai = True  # all identified tools in this schema are AI tools
        intervention_id = _slug(tool_name)

        if primary_intervention_id is None:
            primary_intervention_id = intervention_id

        db_session.run(
            """
            MERGE (i:Intervention {intervention_id: $intervention_id})
            ON CREATE SET
                i.name = $name,
                i.is_ai_powered = $is_ai_powered,
                i.is_named_product = $is_named_product
            WITH i
            MATCH (p:Paper {title: $title})
            MERGE (p)-[r:EVALUATES]->(i)
            SET r.role = 'primary',
                r.use_case = $use_case
            """,
            {
                "intervention_id": intervention_id,
                "name": tool_name,
                "is_ai_powered": is_ai,
                "is_named_product": is_named,
                "title": title,
                "use_case": use_case,
            },
        )

        # ── EmpiricalFinding nodes from tool.findings[] ───────────────────────
        findings = _get(tool, "findings") or []
        for idx, finding in enumerate(findings):
            outcome_name = _get(finding, "outcome_category", "")
            if not outcome_name:
                continue

            finding_id = f"finding_{abs(hash(str(title) + tool_name + outcome_name + str(idx))) % 10_000_000}"

            # Paper → Outcome (direct failsafe link)
            db_session.run(
                """
                MATCH (p:Paper {title: $title})
                MATCH (out:Outcome {name: $outcome_name})
                MERGE (p)-[r:FOCUSES_ON_OUTCOME]->(out)
                """,
                {"title": title, "outcome_name": outcome_name},
            )

            # EmpiricalFinding node
            db_session.run(
                """
                MATCH (p:Paper {title: $title})
                MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                ON CREATE SET
                    f.direction = $direction,
                    f.finding_summary = $finding_summary,
                    f.finding_type = $finding_type,
                    f.measure = $measure,
                    f.sample_size = $sample_size,
                    f.effect_size = $effect_size,
                    f.confidence_interval = $confidence_interval
                MERGE (p)-[:REPORTS_FINDING]->(f)
                """,
                {
                    "title": title,
                    "finding_id": finding_id,
                    "direction": _get(finding, "direction", ""),
                    "finding_summary": _get(finding, "finding_summary", ""),
                    "finding_type": _get(finding, "finding_type", "primary"),
                    "measure": _get(finding, "measure", "not_reported"),
                    "sample_size": _get(finding, "sample_size", "not_reported"),
                    "effect_size": _get(finding, "effect_size", "not_reported"),
                    "confidence_interval": _get(finding, "confidence_interval", "not_reported"),
                },
            )

            # EmpiricalFinding → Outcome
            db_session.run(
                """
                MATCH (out:Outcome {name: $outcome_name})
                MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                MERGE (f)-[:TARGETS_OUTCOME]->(out)
                """,
                {"outcome_name": outcome_name, "finding_id": finding_id},
            )

            # Tool → EmpiricalFinding
            db_session.run(
                """
                MATCH (i:Intervention {intervention_id: $intervention_id})
                MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                MERGE (i)-[:PRODUCES_FINDING]->(f)
                """,
                {"intervention_id": intervention_id, "finding_id": finding_id},
            )

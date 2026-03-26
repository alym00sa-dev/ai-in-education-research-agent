"""KG v2 migration script.

Migrates the Neo4j knowledge graph from the old 12-outcome schema to the new 9-outcome schema.
Safe to run multiple times (idempotent).

Changes:
  1. Create 9 new Outcome nodes (idempotent MERGE)
  2. Rename 1:1 mapped Outcome nodes (update id + name properties)
  3. Merge many→1 Outcome nodes (retarget all relationships, delete old nodes)
  4. Create "Academic — Other" and "Systemic / Institutional Impact" (new, no existing papers)
  5. Delete ImplementationObjective nodes + HAS_IMPLEMENTATION_OBJECTIVE + TARGETS_OUTCOME rels
  6. EmpiricalFinding: rename results_summary → finding_summary; drop old demographic fields
  7. Paper nodes: add default values for new fields (quality_tier="", impact_tier="", etc.)

Run from the research_assistant_agent/ directory:
    python scripts/migrate_kg_v2.py
"""

import sys
import os

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.neo4j_config import get_neo4j_connection

# ── Outcome mapping ────────────────────────────────────────────────────────────

# 1:1 renames — old id → new name
ONE_TO_ONE = {
    "Cognitive - Reading and writing literacy":             "Academic — Literacy",
    "Cognitive - speaking, listening, and language fluency": "Academic — Language Fluency",
    "Cognitive - Mathematical numeracy":                   "Academic — Mathematical Numeracy",
    "Cognitive - Scientific Reasoning":                    "Academic — Scientific Reasoning",
}

# Many→1 merges — list of old ids → new name
MANY_TO_ONE = {
    "Durable Skills": [
        "Cognitive - Critical Thinking/Metacognitive skills",
        "Behavioral - study habits, concentration",
    ],
    "Operational Efficiency": [
        "Behavioral - task and assignment efficiency",
        "Behavioral - productivity",
    ],
    "Social-Emotional Skills": [
        "Behavioral - participation and social engagement",
        "Affective - motivation",
        "Affective - engagement",
        "Affective - persistence",
    ],
}

# New outcome nodes with no existing papers
NEW_OUTCOMES = [
    "Academic — Other",
    "Systemic / Institutional Impact",
]

# Old demographic / scoring fields to remove from EmpiricalFinding nodes
FINDING_FIELDS_TO_REMOVE = [
    "student_racial_makeup",
    "student_socioeconomic_makeup",
    "student_gender_makeup",
    "student_age_distribution",
    "school_type",
    "public_private_status",
    "title_i_status",
    "ses_indicator",
    "ses_numeric",
    "special_education_services",
    "urban_type",
    "governance_type",
    "institutional_level",
    "postsecondary_type",
    "region",
    "system_impact_levels",
    "decision_making_complexity",
    "evidence_type_strength",
    "evaluation_burden_cost",
    "results_summary",  # renamed to finding_summary
]


def run(dry_run: bool = False):
    conn = get_neo4j_connection()

    def execute(label: str, query: str, params: dict = None):
        if dry_run:
            print(f"  [DRY RUN] {label}")
            return []
        result = conn.execute_query(query, params or {})
        print(f"  ✅ {label}")
        return result

    print("\n═══ KG v2 Migration ═══\n")

    # ── Phase 1: Create merge-target Outcome nodes ─────────────────────────────
    print("Phase 1 — Create new Outcome nodes (merge targets + brand-new)...")
    all_new_outcomes = list(MANY_TO_ONE.keys()) + NEW_OUTCOMES
    for name in all_new_outcomes:
        execute(
            f"MERGE Outcome: {name}",
            "MERGE (o:Outcome {name: $name}) ON CREATE SET o.id = $name",
            {"name": name},
        )

    # ── Phase 2: 1:1 renames ──────────────────────────────────────────────────
    print("\nPhase 2 — Rename 1:1 Outcome nodes...")
    for old_id, new_name in ONE_TO_ONE.items():
        execute(
            f"Rename '{old_id}' → '{new_name}'",
            """
            MATCH (o:Outcome {id: $old_id})
            SET o.id = $new_name, o.name = $new_name
            """,
            {"old_id": old_id, "new_name": new_name},
        )

    # ── Phase 3: Many→1 merges ─────────────────────────────────────────────────
    print("\nPhase 3 — Merge many-to-one Outcome nodes...")
    for new_name, old_ids in MANY_TO_ONE.items():
        for old_id in old_ids:
            # Retarget FOCUSES_ON_OUTCOME relationships
            execute(
                f"Retarget FOCUSES_ON_OUTCOME: '{old_id}' → '{new_name}'",
                """
                MATCH (old_out:Outcome {id: $old_id})
                MATCH (new_out:Outcome {name: $new_name})
                MATCH (p:Paper)-[r:FOCUSES_ON_OUTCOME]->(old_out)
                MERGE (p)-[nr:FOCUSES_ON_OUTCOME]->(new_out)
                  ON CREATE SET nr.confidence = coalesce(r.confidence, 0.7)
                DELETE r
                """,
                {"old_id": old_id, "new_name": new_name},
            )
            # Retarget HAS_FINDING relationships
            execute(
                f"Retarget HAS_FINDING: '{old_id}' → '{new_name}'",
                """
                MATCH (old_out:Outcome {id: $old_id})
                MATCH (new_out:Outcome {name: $new_name})
                MATCH (old_out)-[r:HAS_FINDING]->(f:EmpiricalFinding)
                MERGE (new_out)-[:HAS_FINDING]->(f)
                DELETE r
                """,
                {"old_id": old_id, "new_name": new_name},
            )
            # Delete the now-empty old Outcome node
            execute(
                f"Delete old Outcome node: '{old_id}'",
                "MATCH (o:Outcome {id: $old_id}) DETACH DELETE o",
                {"old_id": old_id},
            )

    # ── Phase 4: Delete ImplementationObjective nodes ─────────────────────────
    print("\nPhase 4 — Delete ImplementationObjective nodes + relationships...")
    execute(
        "Delete all ImplementationObjective nodes and their relationships",
        "MATCH (io:ImplementationObjective) DETACH DELETE io",
    )

    # ── Phase 5: EmpiricalFinding — rename results_summary → finding_summary ──
    print("\nPhase 5 — EmpiricalFinding: rename results_summary → finding_summary...")
    execute(
        "Copy results_summary → finding_summary on all EmpiricalFinding nodes",
        """
        MATCH (f:EmpiricalFinding)
        WHERE f.results_summary IS NOT NULL AND f.finding_summary IS NULL
        SET f.finding_summary = f.results_summary
        """,
    )

    # ── Phase 6: EmpiricalFinding — drop old demographic/scoring fields ────────
    print("\nPhase 6 — EmpiricalFinding: remove old fields...")
    remove_clause = ", ".join(f"f.{field}" for field in FINDING_FIELDS_TO_REMOVE)
    execute(
        f"Remove {len(FINDING_FIELDS_TO_REMOVE)} old fields from all EmpiricalFinding nodes",
        f"MATCH (f:EmpiricalFinding) REMOVE {remove_clause}",
    )

    # ── Phase 7: Paper nodes — add default values for new fields ──────────────
    print("\nPhase 7 — Paper nodes: add default values for new fields...")
    execute(
        "Set defaults for quality_tier, impact_tier, extraction_status, source_db, extended_summary",
        """
        MATCH (p:Paper)
        SET
          p.quality_tier     = coalesce(p.quality_tier, ''),
          p.impact_tier      = coalesce(p.impact_tier, ''),
          p.extraction_status = coalesce(p.extraction_status, 'legacy'),
          p.source_db        = coalesce(p.source_db, ''),
          p.extended_summary = coalesce(p.extended_summary, '')
        """,
    )

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n═══ Migration complete ═══")
    if not dry_run:
        counts = conn.get_node_counts()
        print("\nNode counts after migration:")
        for label, count in sorted(counts.items()):
            print(f"  {label}: {count}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("⚠️  DRY RUN — no changes will be made\n")
    run(dry_run=dry_run)

"""Cypher query functions for the KG Agent."""
from typing import List, Dict, Any
from src.neo4j_config import get_neo4j_connection


def get_papers_by_taxonomy(
    objectives: List[str],
    outcomes: List[str],
    populations: List[str],
) -> List[Dict[str, Any]]:
    """Fetch papers matching any of the given taxonomy terms."""
    conn = get_neo4j_connection()
    params: Dict[str, Any] = {
        "objectives": objectives,
        "outcomes": outcomes,
        "populations": populations,
    }
    query = """
    MATCH (p:Paper)
    OPTIONAL MATCH (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
    OPTIONAL MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
    OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
    WHERE
        (size($objectives) = 0 OR io.id IN $objectives)
        OR (size($outcomes) = 0 OR out.id IN $outcomes)
        OR (size($populations) = 0 OR p.population IN $populations)
    RETURN DISTINCT
        p.title          AS title,
        p.year           AS year,
        p.url            AS url,
        p.population     AS population,
        p.study_design   AS study_design,
        io.id            AS objective,
        out.id           AS outcome,
        f.direction      AS finding_direction,
        f.results_summary AS finding_summary,
        f.effect_size    AS effect_size,
        f.study_size     AS study_size
    ORDER BY p.year DESC
    LIMIT 60
    """
    return conn.execute_query(query, params)


def get_outcome_coverage() -> List[Dict[str, Any]]:
    """Return paper counts per outcome node."""
    conn = get_neo4j_connection()
    query = """
    MATCH (p:Paper)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
    RETURN out.id AS outcome, count(p) AS paper_count
    ORDER BY paper_count DESC
    """
    return conn.execute_query(query)


def get_objective_coverage() -> List[Dict[str, Any]]:
    """Return paper counts per implementation objective node."""
    conn = get_neo4j_connection()
    query = """
    MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
    RETURN io.id AS objective, count(p) AS paper_count
    ORDER BY paper_count DESC
    """
    return conn.execute_query(query)


def get_total_paper_count() -> int:
    """Return total number of Paper nodes."""
    conn = get_neo4j_connection()
    result = conn.execute_query("MATCH (p:Paper) RETURN count(p) AS total")
    return result[0]["total"] if result else 0


def query_by_empirical_findings(
    study_designs: List[str] = None,
    finding_directions: List[str] = None,
) -> List[Dict[str, Any]]:
    """Query papers by study design and/or finding direction."""
    conn = get_neo4j_connection()
    conditions = []
    params: Dict[str, Any] = {}
    if study_designs:
        params["designs"] = study_designs
        conditions.append("p.study_design IN $designs")
    if finding_directions:
        params["directions"] = finding_directions
        conditions.append("f.direction IN $directions")
    if not conditions:
        return []
    where_clause = "WHERE " + " OR ".join(conditions)
    query = f"""
    MATCH (p:Paper)
    OPTIONAL MATCH (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
    OPTIONAL MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
    OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
    {where_clause}
    RETURN DISTINCT
        p.title          AS title,
        p.year           AS year,
        p.url            AS url,
        p.population     AS population,
        p.study_design   AS study_design,
        io.id            AS objective,
        out.id           AS outcome,
        f.direction      AS finding_direction,
        f.results_summary AS finding_summary,
        f.effect_size    AS effect_size,
        f.study_size     AS study_size
    ORDER BY p.year DESC
    LIMIT 60
    """
    return conn.execute_query(query, params)

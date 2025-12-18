"""Evidence gap map visualization for research papers."""
from typing import List, Dict, Any
import pandas as pd
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from src.neo4j_config import get_neo4j_connection, IMPLEMENTATION_OBJECTIVES, OUTCOMES

load_dotenv()


def get_evidence_map_data() -> pd.DataFrame:
    """Query Neo4j to get paper counts by Implementation Objective × Outcome.

    Returns:
        DataFrame with columns: implementation_objective, outcome, count
    """
    conn = get_neo4j_connection()

    query = """
    MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
    MATCH (p)-[:FOCUSES_ON_OUTCOME]->(o:Outcome)
    RETURN io.id as implementation_objective,
           o.id as outcome,
           count(p) as count
    ORDER BY io.id, o.id
    """

    results = conn.execute_query(query)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # If no data, return empty DataFrame with correct columns
    if df.empty:
        df = pd.DataFrame(columns=['implementation_objective', 'outcome', 'count'])

    return df


def get_paper_details_for_cell(implementation_objective: str, outcome: str) -> List[Dict[str, Any]]:
    """Get comprehensive paper details for a specific Implementation Objective × Outcome cell.

    Args:
        implementation_objective: The implementation objective
        outcome: The outcome focus area

    Returns:
        List of paper dictionaries with all metadata and findings
    """
    conn = get_neo4j_connection()

    query = """
    MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective {id: $io})
    MATCH (p)-[:FOCUSES_ON_OUTCOME]->(o:Outcome {id: $outcome})
    WITH p
    OPTIONAL MATCH (p)-[:TARGETS_POPULATION]->(pop:Population)
    OPTIONAL MATCH (p)-[:TARGETS_USER_TYPE]->(ut:UserType)
    OPTIONAL MATCH (p)-[:USES_STUDY_DESIGN]->(sd:StudyDesign)
    OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
    WITH p,
         COLLECT(DISTINCT pop.id)[0] as population,
         COLLECT(DISTINCT ut.id)[0] as user_type,
         COLLECT(DISTINCT sd.id)[0] as study_design,
         COLLECT(DISTINCT f.direction)[0] as finding_direction,
         COLLECT(DISTINCT f.results_summary)[0] as results_summary,
         COLLECT(DISTINCT f.measure)[0] as measure,
         COLLECT(DISTINCT f.study_size)[0] as study_size,
         COLLECT(DISTINCT f.effect_size)[0] as effect_size
    RETURN p.title as title,
           p.url as url,
           p.year as year,
           p.venue as venue,
           population,
           user_type,
           study_design,
           finding_direction,
           results_summary,
           measure,
           study_size,
           effect_size
    ORDER BY p.year DESC
    """

    results = conn.execute_query(query, {
        'io': implementation_objective,
        'outcome': outcome
    })

    return results


def create_full_matrix() -> pd.DataFrame:
    """Create a full matrix with all combinations, filling in zeros where no papers exist.

    Returns:
        DataFrame with all (Implementation Objective, Outcome) combinations and counts
    """
    # Get actual data
    df = get_evidence_map_data()

    # Create all possible combinations
    all_combinations = []
    for io in IMPLEMENTATION_OBJECTIVES:
        for outcome in OUTCOMES:
            all_combinations.append({
                'implementation_objective': io,
                'outcome': outcome,
                'count': 0
            })

    full_df = pd.DataFrame(all_combinations)

    # Update with actual counts where they exist
    if not df.empty:
        for _, row in df.iterrows():
            mask = (
                (full_df['implementation_objective'] == row['implementation_objective']) &
                (full_df['outcome'] == row['outcome'])
            )
            full_df.loc[mask, 'count'] = row['count']

    return full_df


def synthesize_papers_for_cell(implementation_objective: str, outcome: str, papers: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate an AI synthesis of papers in a cell, identifying overview and gaps.

    Args:
        implementation_objective: The implementation objective
        outcome: The outcome focus area
        papers: List of paper dictionaries with findings

    Returns:
        Dict with 'overview' and 'gaps' keys containing the synthesis
    """
    if not papers:
        return {
            'overview': 'No papers available for this cell.',
            'gaps': 'Unable to identify gaps without research papers.'
        }

    # Build context from papers
    papers_context = []
    for i, paper in enumerate(papers, 1):
        paper_text = f"""
Paper {i}: {paper.get('title', 'Untitled')}
Year: {paper.get('year', 'N/A')}
Study Design: {paper.get('study_design', 'N/A')}
Population: {paper.get('population', 'N/A')}
Finding: {paper.get('results_summary', 'No summary available')}
Direction: {paper.get('finding_direction', 'N/A')}
Measure: {paper.get('measure', 'N/A')}
"""
        papers_context.append(paper_text.strip())

    context = "\n\n".join(papers_context)

    # Create prompt for synthesis
    prompt = f"""You are analyzing research papers in the AI in Education field.

Implementation Objective: {implementation_objective}
Outcome Focus Area: {outcome}

Here are the {len(papers)} papers in this area:

{context}

Please provide:

1. OVERVIEW (2-3 paragraphs):
   - Synthesize the key findings across these papers into a cohesive narrative
   - IMPORTANT: Use parenthetical citations (e.g., "AI-driven feedback significantly enhanced language skills (Paper 1)" or "Mixed results were observed (Papers 2, 3)")
   - Base your synthesis on the "Finding" and "Direction" fields as the main content
   - Use the other fields (Population, Study Design, Measure, etc.) to contextualize and qualify the findings
   - For example: "Among undergraduate students, AI tutoring improved performance (Paper 1)" or "Using a quasi-experimental design with test scores as the measure, researchers found positive effects (Paper 2)"
   - Focus on what the empirical evidence tells us about using {implementation_objective} to affect {outcome}
   - Highlight patterns and convergent/divergent findings across studies
   - Write in an academic synthesis style, not as a list of paper summaries

2. EVIDENCE GAPS (3-5 bullet points maximum):
   - Identify ONLY the most critical and obvious gaps
   - Focus on gaps that are clearly evident from these specific papers
   - Prioritize: missing populations, unexplored contexts, methodological limitations, or contradictory findings that need resolution

Format your response as:

## Overview
[Your overview here with paper citations]

## Evidence Gaps
- [Most critical gap 1]
- [Most critical gap 2]
- [Most critical gap 3]
etc. (3-5 maximum)"""

    try:
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = anthropic_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        synthesis_text = response.content[0].text

        # Parse the response
        overview = ""
        gaps = ""

        if "## Overview" in synthesis_text and "## Evidence Gaps" in synthesis_text:
            parts = synthesis_text.split("## Evidence Gaps")
            overview = parts[0].replace("## Overview", "").strip()
            gaps = parts[1].strip()
        else:
            # Fallback if format is different
            overview = synthesis_text
            gaps = "Unable to parse evidence gaps from synthesis."

        return {
            'overview': overview,
            'gaps': gaps
        }

    except Exception as e:
        return {
            'overview': f"Error generating synthesis: {str(e)}",
            'gaps': "Unable to identify gaps due to synthesis error."
        }

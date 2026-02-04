"""
Import WWC Level 3 data into Neo4j.

This script imports the 67 tech-compatible interventions from WWC,
creating Paper and EmpiricalFinding nodes tagged with source="WWC".
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from src.neo4j_config import get_neo4j_connection, OUTCOMES, IMPLEMENTATION_OBJECTIVES

# Path to files
MAPPED_FILE = Path(__file__).parent / "wwc_level3_mapped.json"
WWC_CSV = Path(__file__).parent.parent / "kg-viz-frontend" / "level-3" / "Interventions_Studies_And_Findings.csv"

# Outcome domain mapping: WWC domains -> Our 12 OUTCOMES
OUTCOME_MAPPING = {
    # Cognitive outcomes
    'Alphabetics': 'Cognitive - Reading and writing literacy',
    'Comprehension': 'Cognitive - Reading and writing literacy',
    'Reading achievement': 'Cognitive - Reading and writing literacy',
    'Reading Fluency': 'Cognitive - Reading and writing literacy',
    'Literacy Achievement': 'Cognitive - Reading and writing literacy',
    'Writing achievement': 'Cognitive - Reading and writing literacy',
    'Writing Quality': 'Cognitive - Reading and writing literacy',
    'Oral language': 'Cognitive - speaking, listening, and language fluency',
    'Language': 'Cognitive - speaking, listening, and language fluency',
    'Language development': 'Cognitive - speaking, listening, and language fluency',
    'English language development': 'Cognitive - speaking, listening, and language fluency',
    'English language proficiency': 'Cognitive - speaking, listening, and language fluency',

    'General Mathematics Achievement': 'Cognitive - Mathematical numeracy',
    'Elementary School Mathematics': 'Cognitive - Mathematical numeracy',
    'Mathematics': 'Cognitive - Mathematical numeracy',
    'Number and Operations': 'Cognitive - Mathematical numeracy',
    'Algebra': 'Cognitive - Mathematical numeracy',
    'Geometry and Measurement': 'Cognitive - Mathematical numeracy',
    'Geometry': 'Cognitive - Mathematical numeracy',

    'Science Achievement': 'Cognitive - Scientific Reasoning',

    'Academic achievement': 'Cognitive - Critical Thinking/Metacognitive skills',
    'General academic achievement (high school)': 'Cognitive - Critical Thinking/Metacognitive skills',
    'General academic achievement (college)': 'Cognitive - Critical Thinking/Metacognitive skills',
    'College Readiness': 'Cognitive - Critical Thinking/Metacognitive skills',

    # Behavioral outcomes
    'Behavior': 'Behavioral - participation and social engagement',
    'External behavior': 'Behavioral - participation and social engagement',
    'Problem behavior': 'Behavioral - participation and social engagement',
    'School engagement': 'Behavioral - participation and social engagement',
    'School Attendance': 'Behavioral - study habits, concentration',
    'Attendance (high school)': 'Behavioral - study habits, concentration',

    'Credit accumulation': 'Behavioral - productivity',
    'Credit accumulation and persistence': 'Behavioral - productivity',
    'Completing school': 'Behavioral - productivity',
    'Progressing in school': 'Behavioral - productivity',

    # Affective outcomes
    'Social-emotional development': 'Affective - motivation',
    'Social-Emotional Learning': 'Affective - motivation',
    'Self-regulation': 'Affective - motivation',

    'Progressing in College': 'Affective - persistence',
    'Staying in School': 'Affective - persistence',
    'Progressing in Developmental Education': 'Affective - persistence',

    'Access and enrollment': 'Affective - engagement',
    'College Enrollment': 'Affective - engagement',

    # Default for unmapped
    'default': 'Cognitive - Critical Thinking/Metacognitive skills'
}


class WWCNeo4jImporter:
    """Import WWC data into Neo4j."""

    def __init__(self):
        self.conn = get_neo4j_connection()
        self.driver = self.conn.driver

        # Load mapped interventions
        with open(MAPPED_FILE, 'r') as f:
            self.interventions = json.load(f)

        # Load raw CSV for detailed data
        self.csv_data = self._load_csv()

        # Group CSV by intervention ID
        self.csv_by_intervention = self._group_csv_by_intervention()

    def _load_csv(self) -> List[Dict]:
        """Load WWC CSV."""
        with open(WWC_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _group_csv_by_intervention(self) -> Dict:
        """Group CSV rows by intervention ID."""
        grouped = {}
        for row in self.csv_data:
            intervention_id = row['i_InterventionID']
            if intervention_id not in grouped:
                grouped[intervention_id] = []
            grouped[intervention_id].append(row)
        return grouped

    def map_outcome_domain(self, wwc_domain: str) -> str:
        """Map WWC outcome domain to our 12 OUTCOMES."""
        return OUTCOME_MAPPING.get(wwc_domain, OUTCOME_MAPPING['default'])

    def infer_evidence_type_strength(self, study_rating: str) -> int:
        """
        Infer evidence_type_strength (0-4 scale, 0=best).
        Based on WWC study rating.
        """
        rating_map = {
            'Meets WWC standards without reservations': 0,
            'Meets WWC standards with reservations': 1,
            'Does not meet WWC standards': 3,
            'Ineligible for review': 4
        }
        return rating_map.get(study_rating, 2)

    def infer_system_impact_levels(self, program_types: Dict) -> int:
        """
        Infer system_impact_levels (0-4 scale).
        Based on program type complexity.
        """
        # More complex program types = higher system impact
        if program_types.get('Policy') or program_types.get('School_level'):
            return 4  # School/district-wide
        elif program_types.get('Curriculum'):
            return 3  # Multiple classrooms
        elif program_types.get('Practice') or program_types.get('Teacher_level'):
            return 2  # Classroom level
        else:
            return 1  # Individual/small group

    def infer_decision_making_complexity(self, program_types: Dict, num_studies: int) -> int:
        """
        Infer decision_making_complexity (0-4 scale).
        Based on implementation scope.
        """
        if program_types.get('Policy'):
            return 4  # Multiple stakeholders at district/state level
        elif program_types.get('School_level'):
            return 3  # School leadership + teachers
        elif program_types.get('Curriculum'):
            return 2  # Admin + teachers
        else:
            return 1  # Teacher-level decision

    def infer_evaluation_burden_cost(self, num_outcomes: int, avg_sample_size: int) -> int:
        """
        Infer evaluation_burden_cost (0-4 scale).
        Based on number of outcomes and sample size needed.
        """
        # More outcomes + larger samples = higher burden
        burden_score = 0

        if num_outcomes >= 5:
            burden_score += 2
        elif num_outcomes >= 3:
            burden_score += 1

        if avg_sample_size >= 1000:
            burden_score += 2
        elif avg_sample_size >= 500:
            burden_score += 1

        return min(4, burden_score)

    def extract_program_types(self, row: Dict, prefix: str) -> Dict:
        """Extract program types from row."""
        return {
            'Curriculum': row.get(f'{prefix}Program_Type_Curriculum') == '1.00',
            'Policy': row.get(f'{prefix}Program_Type_Policy') == '1.00',
            'Practice': row.get(f'{prefix}Program_Type_Practice') == '1.00',
            'School_level': row.get(f'{prefix}Program_Type_School_level') == '1.00',
            'Supplement': row.get(f'{prefix}Program_Type_Supplement') == '1.00',
            'Teacher_level': row.get(f'{prefix}Program_Type_Teacher_level') == '1.00'
        }

    def extract_school_type(self, row: Dict, prefix: str) -> str:
        """Extract school type."""
        types = []
        if row.get(f'{prefix}School_type_Public') == '1.00':
            types.append('Public')
        if row.get(f'{prefix}School_type_Private') == '1.00':
            types.append('Private')
        if row.get(f'{prefix}School_type_Charter') == '1.00':
            types.append('Charter')
        return ', '.join(types) if types else 'not_reported'

    def extract_region(self, row: Dict, prefix: str) -> str:
        """Extract primary region (first state found)."""
        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
                 'Connecticut', 'Delaware', 'DC', 'Florida', 'Georgia', 'Hawaii',
                 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
                 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
                 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska',
                 'Nevada', 'New_Hampshire', 'New_Jersey', 'New_Mexico', 'New_York',
                 'North_Carolina', 'North_Dakota', 'Ohio', 'Oklahoma', 'Oregon',
                 'Pennsylvania', 'Rhode_Island', 'South_Carolina', 'South_Dakota',
                 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
                 'West_Virginia', 'Wisconsin', 'Wyoming']

        for state in states:
            if row.get(f'{prefix}Region_State_{state}') == '1.00':
                return state.replace('_', ' ')
        return 'not_reported'

    def extract_population(self, row: Dict, prefix: str) -> str:
        """Extract population/grade level."""
        # Check grade levels
        if any(row.get(f'{prefix}Grade_{g}') == '1.00' for g in ['PK', 'PS', 'K']):
            return 'Elementary (PreK-5th)'
        elif any(row.get(f'{prefix}Grade_{g}') == '1.00' for g in ['1', '2', '3', '4', '5']):
            return 'Elementary (PreK-5th)'
        elif any(row.get(f'{prefix}Grade_{g}') == '1.00' for g in ['6', '7', '8']):
            return 'Middle School (6th-8th)'
        elif any(row.get(f'{prefix}Grade_{g}') == '1.00' for g in ['9', '10', '11', '12']):
            return 'High School (9th-12th)'

        # Check for postsecondary topics
        if row.get(f'{prefix}Topic_Postsecondary'):
            return 'Undergraduate'

        return 'not_reported'

    def determine_user_type(self, program_types: Dict) -> str:
        """Determine user type based on program characteristics."""
        if program_types.get('Policy'):
            return 'Systematic: social/political level information'
        elif program_types.get('School_level'):
            return 'School'
        elif program_types.get('Teacher_level'):
            return 'Educator'
        else:
            return 'Student'

    def safe_float(self, value) -> Optional[float]:
        """Safely convert to float."""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    def safe_int(self, value) -> Optional[int]:
        """Safely convert to int."""
        try:
            return int(float(value)) if value else None
        except (ValueError, TypeError):
            return None

    def import_intervention(self, intervention: Dict):
        """Import a single intervention with all its studies and findings."""
        intervention_id = intervention['intervention_id']
        intervention_name = intervention['intervention_name']
        io = intervention['implementation_objective']

        print(f"\nImporting: {intervention_name}")
        print(f"  IO: {io}")

        # Get CSV rows for this intervention
        csv_rows = self.csv_by_intervention.get(intervention_id, [])
        if not csv_rows:
            print(f"  ⚠️  No CSV data found, skipping")
            return

        # Group by study
        studies = {}
        for row in csv_rows:
            study_id = row['s_StudyID']
            if not study_id:
                continue

            if study_id not in studies:
                studies[study_id] = {
                    'row': row,
                    'findings': []
                }

            if row['f_FindingID']:
                studies[study_id]['findings'].append(row)

        print(f"  Studies: {len(studies)}, Total findings: {sum(len(s['findings']) for s in studies.values())}")

        # Import each study as a Paper
        for study_id, study_data in studies.items():
            self._import_study(study_id, study_data, intervention_name, io)

    def _import_study(self, study_id: str, study_data: Dict, intervention_name: str, io: str):
        """Import a single study (Paper) with its findings."""
        row = study_data['row']
        findings = study_data['findings']

        # Extract metadata
        citation = row['s_Citation'][:500] if row['s_Citation'] else f"WWC Study {study_id}"
        study_design = row['s_Study_Design'] if row['s_Study_Design'] else 'Randomized Control Trial'
        study_rating = row['s_Study_Rating']
        publication_date = row['s_Publication_Date']
        url = row['s_Study_Page_URL']

        # Extract year from publication date
        year = None
        if publication_date:
            try:
                year = int(publication_date.split('-')[0])
            except:
                year = 2020  # Default

        # Extract context
        program_types = self.extract_program_types(row, 's_')
        school_type = self.extract_school_type(row, 's_')
        region = self.extract_region(row, 's_')
        population = self.extract_population(row, 's_')
        user_type = self.determine_user_type(program_types)

        # Create Paper node
        paper_id = f"wwc_{study_id}"

        with self.driver.session() as session:
            session.run("""
                MERGE (p:Paper {title: $title})
                ON CREATE SET
                    p.paper_id = $paper_id,
                    p.year = $year,
                    p.venue = $venue,
                    p.url = $url,
                    p.session_id = $session_id,
                    p.added_date = $added_date,
                    p.population = $population,
                    p.user_type = $user_type,
                    p.study_design = $study_design,
                    p.source = $source,
                    p.wwc_study_id = $wwc_study_id,
                    p.wwc_study_rating = $wwc_study_rating
                ON MATCH SET
                    p.source = $source,
                    p.wwc_study_id = $wwc_study_id,
                    p.wwc_study_rating = $wwc_study_rating
            """,
                title=citation,
                paper_id=paper_id,
                year=year,
                venue="What Works Clearinghouse",
                url=url or "",
                session_id="wwc_import",
                added_date=datetime.now().isoformat(),
                population=population,
                user_type=user_type,
                study_design=study_design,
                source="WWC",
                wwc_study_id=study_id,
                wwc_study_rating=study_rating
            )

            # Link to Implementation Objective
            session.run("""
                MATCH (p:Paper {paper_id: $paper_id})
                MATCH (io:ImplementationObjective {type: $io_type})
                MERGE (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io)
            """,
                paper_id=paper_id,
                io_type=io
            )

        # Import findings
        for finding_row in findings:
            self._import_finding(paper_id, finding_row, program_types, len(findings))

    def _import_finding(self, paper_id: str, finding_row: Dict, program_types: Dict, total_findings: int):
        """Import a single finding (EmpiricalFinding)."""
        finding_id = f"wwc_{finding_row['f_FindingID']}"
        outcome_domain = finding_row['f_Outcome_Domain']
        outcome_measure = finding_row['f_Outcome_Measure']
        effect_size = self.safe_float(finding_row['f_Effect_Size_WWC'])
        is_significant = finding_row['f_Is_Statistically_Significant'] == 'True'
        sample_size = self.safe_int(finding_row['f_Outcome_Sample_Size'])
        finding_rating = finding_row['f_Finding_Rating']
        favorable = finding_row['f_FavorableUnfavorableDesignation']

        # Map outcome
        mapped_outcome = self.map_outcome_domain(outcome_domain)

        # Determine direction based on effect size and favorability
        if effect_size is not None:
            if effect_size > 0.1:
                direction = "Positive"
            elif effect_size < -0.1:
                direction = "Negative"
            else:
                direction = "No Effect"
        else:
            direction = "Mixed"

        # Infer missing metrics
        study_rating = finding_row['s_Study_Rating']
        evidence_type_strength = self.infer_evidence_type_strength(study_rating)
        system_impact_levels = self.infer_system_impact_levels(program_types)
        decision_making_complexity = self.infer_decision_making_complexity(program_types, 1)
        evaluation_burden_cost = self.infer_evaluation_burden_cost(total_findings, sample_size or 0)

        # Extract context
        school_type = self.extract_school_type(finding_row, 's_')
        region = self.extract_region(finding_row, 's_')

        with self.driver.session() as session:
            # Create Finding node
            session.run("""
                MATCH (p:Paper {paper_id: $paper_id})
                MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                ON CREATE SET
                    f.direction = $direction,
                    f.results_summary = $results_summary,
                    f.measure = $measure,
                    f.study_size = $study_size,
                    f.effect_size = $effect_size,
                    f.school_type = $school_type,
                    f.region = $region,
                    f.system_impact_levels = $system_impact_levels,
                    f.decision_making_complexity = $decision_making_complexity,
                    f.evidence_type_strength = $evidence_type_strength,
                    f.evaluation_burden_cost = $evaluation_burden_cost,
                    f.source = $source,
                    f.wwc_finding_rating = $wwc_finding_rating,
                    f.wwc_is_significant = $wwc_is_significant
                MERGE (p)-[:REPORTS_FINDING]->(f)
            """,
                paper_id=paper_id,
                finding_id=finding_id,
                direction=direction,
                results_summary=f"Effect size: {effect_size:.3f}" if effect_size else "See WWC",
                measure=outcome_measure or outcome_domain,
                study_size=sample_size,
                effect_size=effect_size,
                school_type=school_type,
                region=region,
                system_impact_levels=system_impact_levels,
                decision_making_complexity=decision_making_complexity,
                evidence_type_strength=evidence_type_strength,
                evaluation_burden_cost=evaluation_burden_cost,
                source="WWC",
                wwc_finding_rating=finding_rating,
                wwc_is_significant=is_significant
            )

            # Link to Outcome
            session.run("""
                MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                MATCH (p:Paper)-[:REPORTS_FINDING]->(f)
                MATCH (o:Outcome {name: $outcome_name})
                MERGE (p)-[:FOCUSES_ON_OUTCOME]->(o)
            """,
                finding_id=finding_id,
                outcome_name=mapped_outcome
            )

    def run_import(self):
        """Run the full import process."""
        print("=" * 80)
        print("IMPORTING WWC LEVEL 3 DATA TO NEO4J")
        print("=" * 80)
        print(f"\nTotal interventions to import: {len(self.interventions)}")

        for i, intervention in enumerate(self.interventions, 1):
            print(f"\n[{i}/{len(self.interventions)}]", end=" ")
            try:
                self.import_intervention(intervention)
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        print("\n" + "=" * 80)
        print("IMPORT COMPLETE")
        print("=" * 80)

        # Get counts
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})
                RETURN count(p) as paper_count
            """)
            paper_count = result.single()['paper_count']

            result = session.run("""
                MATCH (f:EmpiricalFinding {source: 'WWC'})
                RETURN count(f) as finding_count
            """)
            finding_count = result.single()['finding_count']

        print(f"\nImported:")
        print(f"  Papers (studies): {paper_count}")
        print(f"  Findings: {finding_count}")
        print(f"\nAll nodes tagged with source='WWC'")
        print(f"\nTo remove all WWC data:")
        print(f"  MATCH (n {{source: 'WWC'}}) DETACH DELETE n")


def main():
    """Main import process."""
    importer = WWCNeo4jImporter()
    importer.run_import()


if __name__ == "__main__":
    main()

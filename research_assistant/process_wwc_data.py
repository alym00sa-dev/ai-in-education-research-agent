"""
Process WWC CSV data for Level 3 visualization.

This script:
1. Parses the WWC Interventions, Studies, and Findings CSV
2. Groups findings by unique StudyID and InterventionID
3. Calculates Level 3 metrics:
   - X-axis: Evidence Base Quality (0-100)
   - Y-axis: External Validity Score
   - Bubble Size: Studies × Sample Size
4. Maps interventions to broadened Implementation Objectives
5. Generates a validation report
"""

import csv
import json
from collections import defaultdict
from typing import Dict, List, Any
from pathlib import Path

# Path to WWC CSV
WWC_CSV_PATH = Path(__file__).parent.parent / "kg-viz-frontend" / "level-3" / "Interventions_Studies_And_Findings.csv"

# Broadened Implementation Objectives (to include non-AI tech)
BROADENED_IOS = [
    "Adaptive Instruction & Tutoring Systems",
    "Personalized Learning & Advising Systems",
    "Data-Driven Decision Support",
    "Learning Pathways & Mobility Support"
]


class WWCDataProcessor:
    """Process WWC data for Level 3 visualization."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.raw_data = []
        self.interventions = defaultdict(lambda: {
            'studies': {},
            'findings': [],
            'intervention_data': None
        })

    def load_data(self):
        """Load CSV data into memory."""
        print(f"Loading data from {self.csv_path}...")
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.raw_data = list(reader)
        print(f"✅ Loaded {len(self.raw_data)} rows")

    def group_by_intervention(self):
        """Group findings by intervention and study."""
        print("\nGrouping data by intervention and study...")

        for row in self.raw_data:
            intervention_id = row['i_InterventionID']
            intervention_name = row['i_Intervention_Name']
            study_id = row['s_StudyID']

            # Store intervention-level data (first occurrence)
            if self.interventions[intervention_id]['intervention_data'] is None:
                self.interventions[intervention_id]['intervention_data'] = {
                    'id': intervention_id,
                    'name': intervention_name,
                    'protocol': row['i_Protocol'],
                    'outcome_domain': row['i_Outcome_Domain'],
                    'num_studies_meeting_standards': row['i_NumStudiesMeetingStandards'],
                    'num_studies_eligible': row['i_NumStudiesEligible'],
                    'effectiveness_rating': row['i_Effectiveness_Rating'],
                    'url': row['i_Intervention_Page_URL'],
                    'sample_size_intervention': row['i_Sample_Size_Intervention']
                }

            # Store study-level data
            if study_id and study_id not in self.interventions[intervention_id]['studies']:
                self.interventions[intervention_id]['studies'][study_id] = {
                    'study_id': study_id,
                    'citation': row['s_Citation'],
                    'intervention_name': row['s_Intervention_Name'],
                    'study_design': row['s_Study_Design'],
                    'study_rating': row['s_Study_Rating'],
                    'publication_date': row['s_Publication_Date'],
                    'url': row['s_Study_Page_URL'],
                    # Demographics
                    'demographics': self._extract_demographics(row, 's_'),
                    'regions': self._extract_regions(row, 's_'),
                    'school_types': self._extract_school_types(row, 's_'),
                    'grade_levels': self._extract_grade_levels(row, 's_'),
                    'urbanicity': self._extract_urbanicity(row, 's_'),
                }

            # Store finding-level data
            if row['f_FindingID']:
                self.interventions[intervention_id]['findings'].append({
                    'finding_id': row['f_FindingID'],
                    'study_id': study_id,
                    'outcome_measure': row['f_Outcome_Measure'],
                    'outcome_domain': row['f_Outcome_Domain'],
                    'effect_size_wwc': self._safe_float(row['f_Effect_Size_WWC']),
                    'effect_size_study': self._safe_float(row['f_Effect_Size_Study']),
                    'is_statistically_significant': row['f_Is_Statistically_Significant'] == 'True',
                    'outcome_sample_size': self._safe_int(row['f_Outcome_Sample_Size']),
                    'finding_rating': row['f_Finding_Rating'],
                    'favorable_unfavorable': row['f_FavorableUnfavorableDesignation']
                })

        print(f"✅ Grouped into {len(self.interventions)} interventions")

    def calculate_metrics(self) -> List[Dict[str, Any]]:
        """Calculate Level 3 metrics for each intervention."""
        print("\nCalculating Level 3 metrics...")

        results = []
        for intervention_id, data in self.interventions.items():
            intervention_info = data['intervention_data']
            studies = data['studies']
            findings = data['findings']

            if not intervention_info or not studies or not findings:
                continue

            # X-axis: Evidence Base Quality (0-100)
            evidence_quality = self._calculate_evidence_quality(studies, findings)

            # Y-axis: External Validity Score
            external_validity = self._calculate_external_validity(studies)

            # Bubble Size: Studies × Sample Size
            bubble_size = self._calculate_bubble_size(studies, findings)

            # Additional breakdown data
            breakdown = self._calculate_breakdown(intervention_info, studies, findings)

            results.append({
                'intervention_id': intervention_id,
                'intervention_name': intervention_info['name'],
                'evidence_quality': evidence_quality,
                'external_validity': external_validity,
                'bubble_size': bubble_size,
                'num_studies': len(studies),
                'num_findings': len(findings),
                'implementation_objective': None,  # To be mapped
                'breakdown': breakdown
            })

        print(f"✅ Calculated metrics for {len(results)} interventions")
        return results

    def _calculate_evidence_quality(self, studies: Dict, findings: List) -> float:
        """
        Calculate Evidence Base Quality (0-100).

        Components:
        1. Study Design Quality (25 pts) - WWC ratings
        2. Replication Strength (25 pts) - Number of studies
        3. Sample Adequacy (25 pts) - Total sample sizes
        4. Effect Consistency (25 pts) - Consistency of effects
        """
        if not studies or not findings:
            return 0.0

        # 1. Study Design Quality (25 pts)
        study_quality_scores = {
            'Meets WWC standards without reservations': 25,
            'Meets WWC standards with reservations': 15,
            'Does not meet WWC standards': 5,
            'Ineligible for review': 0
        }

        study_ratings = [study_quality_scores.get(s['study_rating'], 0)
                        for s in studies.values() if s['study_rating']]
        design_quality = sum(study_ratings) / len(study_ratings) if study_ratings else 0

        # 2. Replication Strength (25 pts)
        num_studies = len(studies)
        if num_studies >= 4:
            replication_score = 25
        elif num_studies == 3:
            replication_score = 20
        elif num_studies == 2:
            replication_score = 15
        else:
            replication_score = 5

        # 3. Sample Adequacy (25 pts)
        total_sample = sum(f['outcome_sample_size'] for f in findings
                          if f['outcome_sample_size'])
        # Normalize: 500+ students = 25 pts
        sample_score = min(25, (total_sample / 500) * 25) if total_sample else 0

        # 4. Effect Consistency (25 pts)
        effect_sizes = [f['effect_size_wwc'] for f in findings
                       if f['effect_size_wwc'] is not None]
        if len(effect_sizes) > 1:
            import statistics
            std_dev = statistics.stdev(effect_sizes)
            # Lower std dev = more consistent = higher score
            # Std dev of 0.2 or less = full 25 pts
            consistency_score = max(0, 25 - (std_dev * 100))
        elif len(effect_sizes) == 1:
            consistency_score = 15  # Single finding, moderate score
        else:
            consistency_score = 0

        total = design_quality + replication_score + sample_score + consistency_score
        return round(total, 2)

    def _calculate_external_validity(self, studies: Dict) -> float:
        """
        Calculate External Validity Score.

        Measures diversity across:
        - Geographic regions
        - School types
        - Demographics (ELL, FRPL, race)
        - Grade levels
        - Urbanicity

        Higher score = more generalizable
        """
        if not studies:
            return 0.0

        # Aggregate across all studies
        all_regions = set()
        all_school_types = set()
        all_grade_levels = set()
        all_urbanicity = set()
        has_ell = False
        has_frpl = False
        racial_diversity = set()

        for study in studies.values():
            all_regions.update(study['regions'])
            all_school_types.update(study['school_types'])
            all_grade_levels.update(study['grade_levels'])
            all_urbanicity.update(study['urbanicity'])

            if study['demographics'].get('ELL'):
                has_ell = True
            if study['demographics'].get('FRPL'):
                has_frpl = True

            # Count racial diversity
            demo = study['demographics']
            for race in ['Asian', 'Black', 'White', 'Hispanic', 'Native_American', 'Pacific_Islander']:
                if demo.get(race):
                    racial_diversity.add(race)

        # Calculate score components
        region_score = min(10, len(all_regions))  # Max 10 pts
        school_type_score = min(5, len(all_school_types) * 1.67)  # Max 5 pts (3 types)
        grade_score = min(10, len(all_grade_levels) * 0.67)  # Max 10 pts (15 grades)
        urbanicity_score = min(5, len(all_urbanicity) * 1.67)  # Max 5 pts (3 types)
        demo_score = (
            (5 if has_ell else 0) +
            (5 if has_frpl else 0) +
            min(10, len(racial_diversity) * 2)  # Max 10 pts
        )

        total = region_score + school_type_score + grade_score + urbanicity_score + demo_score
        return round(total, 2)

    def _calculate_bubble_size(self, studies: Dict, findings: List) -> float:
        """Calculate bubble size: Studies × Average Sample Size."""
        num_studies = len(studies)
        total_sample = sum(f['outcome_sample_size'] for f in findings
                          if f['outcome_sample_size'])
        avg_sample = total_sample / len(findings) if findings else 0

        size = num_studies * avg_sample
        return round(size, 2)

    def _calculate_breakdown(self, intervention_info: Dict, studies: Dict,
                            findings: List) -> Dict[str, Any]:
        """Calculate detailed breakdown data for popup."""

        # Effect sizes
        effect_sizes = [f['effect_size_wwc'] for f in findings
                       if f['effect_size_wwc'] is not None]
        avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

        # Outcome domains
        outcome_domains = list(set(f['outcome_domain'] for f in findings
                                  if f['outcome_domain']))

        # Statistical significance rate
        sig_findings = sum(1 for f in findings if f['is_statistically_significant'])
        sig_rate = (sig_findings / len(findings) * 100) if findings else 0

        return {
            'wwc_effectiveness_rating': intervention_info['effectiveness_rating'],
            'num_studies': len(studies),
            'num_findings': len(findings),
            'total_sample_size': sum(f['outcome_sample_size'] for f in findings
                                    if f['outcome_sample_size']),
            'avg_effect_size': round(avg_effect, 3),
            'effect_sizes': effect_sizes,
            'outcome_domains': outcome_domains,
            'statistical_significance_rate': round(sig_rate, 1),
            'intervention_url': intervention_info['url']
        }

    # Helper methods
    def _extract_demographics(self, row: Dict, prefix: str) -> Dict:
        """Extract demographic data from row."""
        return {
            'ELL': row.get(f'{prefix}Demographics_Sample_ELL') == '1.00',
            'FRPL': row.get(f'{prefix}Demographics_Sample_FRPL') == '1.00',
            'International': row.get(f'{prefix}Demographics_Sample_International') == '1.00',
            'Hispanic': row.get(f'{prefix}Ethnicity_Hispanic') == '1.00',
            'Asian': row.get(f'{prefix}Race_Asian') == '1.00',
            'Black': row.get(f'{prefix}Race_Black') == '1.00',
            'Native_American': row.get(f'{prefix}Race_Native_American') == '1.00',
            'Pacific_Islander': row.get(f'{prefix}Race_Pacific_Islander') == '1.00',
            'White': row.get(f'{prefix}Race_White') == '1.00',
        }

    def _extract_regions(self, row: Dict, prefix: str) -> List[str]:
        """Extract regions where study was conducted."""
        regions = []
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
                regions.append(state)

        return regions

    def _extract_school_types(self, row: Dict, prefix: str) -> List[str]:
        """Extract school types."""
        types = []
        for stype in ['Charter', 'Parochial', 'Private', 'Public']:
            if row.get(f'{prefix}School_type_{stype}') == '1.00':
                types.append(stype)
        return types

    def _extract_grade_levels(self, row: Dict, prefix: str) -> List[str]:
        """Extract grade levels."""
        grades = []
        for grade in ['PK', 'PS', 'K', '1', '2', '3', '4', '5', '6', '7', '8',
                     '9', '10', '11', '12']:
            if row.get(f'{prefix}Grade_{grade}') == '1.00':
                grades.append(grade)
        return grades

    def _extract_urbanicity(self, row: Dict, prefix: str) -> List[str]:
        """Extract urbanicity types."""
        types = []
        for utype in ['Rural', 'Suburban', 'Urban']:
            if row.get(f'{prefix}Urbanicity_{utype}') == '1.00':
                types.append(utype)
        return types

    def _safe_float(self, value: str) -> float:
        """Safely convert string to float."""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    def _safe_int(self, value: str) -> int:
        """Safely convert string to int."""
        try:
            return int(float(value)) if value else None
        except (ValueError, TypeError):
            return None


def main():
    """Main processing pipeline."""
    processor = WWCDataProcessor(WWC_CSV_PATH)

    # Load and process data
    processor.load_data()
    processor.group_by_intervention()
    results = processor.calculate_metrics()

    # Generate report
    print("\n" + "=" * 70)
    print("LEVEL 3 METRICS REPORT")
    print("=" * 70)

    print(f"\nTotal interventions processed: {len(results)}")

    # Sort by evidence quality
    results.sort(key=lambda x: x['evidence_quality'], reverse=True)

    print("\nTop 10 interventions by Evidence Quality:")
    for i, result in enumerate(results[:10], 1):
        print(f"\n{i}. {result['intervention_name']}")
        print(f"   Evidence Quality: {result['evidence_quality']:.1f}/100")
        print(f"   External Validity: {result['external_validity']:.1f}")
        print(f"   Bubble Size: {result['bubble_size']:.0f}")
        print(f"   Studies: {result['num_studies']}, Findings: {result['num_findings']}")

    # Save results to JSON
    output_path = Path(__file__).parent / "wwc_level3_metrics.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to {output_path}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Review the metrics report above")
    print("2. Map interventions to broadened Implementation Objectives")
    print("3. Filter for technology-related interventions")
    print("4. Import into Neo4j with 'WWC' tag")


if __name__ == "__main__":
    main()

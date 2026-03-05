"""
Map WWC interventions to broadened Implementation Objectives.

This identifies tech-compatible interventions and maps them to:
1. Adaptive Instruction & Tutoring Systems
2. Personalized Learning & Advising Systems
3. Data-Driven Decision Support
4. Learning Pathways & Mobility Support
"""

import json
import re
from typing import Optional, List

# Broadened Implementation Objectives
IOS = {
    'tutoring': 'Adaptive Instruction & Tutoring Systems',
    'personalized': 'Personalized Learning & Advising Systems',
    'decision': 'Data-Driven Decision Support',
    'mobility': 'Learning Pathways & Mobility Support'
}

# Mapping rules based on intervention characteristics
MAPPING_RULES = {
    'tutoring': {
        'keywords': [
            'tutor', 'instruction', 'teaching', 'curriculum', 'pedagogy',
            'reading program', 'math program', 'science program',
            'literacy', 'numeracy', 'adaptive', 'intelligent',
            'supplemental', 'intervention', 'remedial', 'enrichment',
            'direct instruction', 'explicit instruction', 'guided',
            'phonics', 'comprehension', 'fluency', 'algebra', 'geometry',
            'writing', 'vocabulary', 'stem', 'steam'
        ],
        'description': 'Instructional programs, curricula, and teaching methods that could be technology-enhanced (adaptive software, intelligent tutoring systems, CAI)'
    },
    'personalized': {
        'keywords': [
            'personal', 'individual', 'differentiat', 'customize',
            'advising', 'counsel', 'mentor', 'coach', 'support',
            'pathway', 'plan', 'goal', 'self-paced', 'flexible',
            'student-centered', 'learner-centered', 'choice',
            'adaptive', 'response to intervention', 'rti'
        ],
        'description': 'Personalized learning approaches, advising systems, and student support that could use adaptive technology or data-driven personalization'
    },
    'decision': {
        'keywords': [
            'assessment', 'data', 'analytics', 'evaluation', 'monitor',
            'dashboard', 'report', 'track', 'progress', 'formative',
            'diagnostic', 'benchmark', 'accountability', 'feedback',
            'professional development', 'teacher training', 'coaching',
            'observation', 'certification', 'leadership', 'principal',
            'administrator', 'policy', 'governance', 'management'
        ],
        'description': 'Assessment systems, teacher effectiveness tools, and decision support that could use dashboards, analytics, or data platforms'
    },
    'mobility': {
        'keywords': [
            'college', 'postsecondary', 'transition', 'pathway',
            'completion', 'persistence', 'retention', 'graduation',
            'enrollment', 'access', 'advising', 'credit', 'transfer',
            'credential', 'degree', 'career', 'readiness', 'preparation',
            'bridge', 'dual enrollment', 'early college', 'acceleration',
            'remedial', 'developmental education'
        ],
        'description': 'Programs supporting educational pathways, college access, completion, and transitions that could use recommendation systems or tracking tools'
    }
}


class WWCtoIOMapper:
    """Map WWC interventions to Implementation Objectives."""

    def __init__(self, metrics_file: str):
        with open(metrics_file, 'r') as f:
            self.interventions = json.load(f)

    def map_intervention(self, intervention: dict) -> Optional[str]:
        """
        Map a single intervention to an Implementation Objective.
        Returns the IO name or None if not tech-compatible.
        """
        # Check for manual override first
        if '_manual_override' in intervention:
            return intervention['_manual_override']

        name = intervention['intervention_name'].lower()

        # Score each IO based on keyword matches
        scores = {}
        for io_key, rules in MAPPING_RULES.items():
            score = 0
            for keyword in rules['keywords']:
                if keyword in name:
                    score += 1
            scores[io_key] = score

        # Get the IO with highest score
        max_score = max(scores.values())

        # Require at least 1 match to be considered tech-compatible
        if max_score >= 1:
            best_io_key = max(scores, key=scores.get)
            return IOS[best_io_key]

        return None

    def map_all(self) -> dict:
        """Map all interventions and generate statistics."""
        results = {
            'mapped': [],
            'unmapped': [],
            'by_io': {io: [] for io in IOS.values()}
        }

        for intervention in self.interventions:
            io = self.map_intervention(intervention)

            if io:
                intervention['implementation_objective'] = io
                results['mapped'].append(intervention)
                results['by_io'][io].append(intervention)
            else:
                results['unmapped'].append(intervention)

        return results

    def generate_report(self, results: dict):
        """Generate a human-readable report."""
        print("=" * 80)
        print("WWC INTERVENTION MAPPING REPORT")
        print("=" * 80)

        total = len(self.interventions)
        mapped = len(results['mapped'])
        unmapped = len(results['unmapped'])

        print(f"\nTotal interventions: {total}")
        print(f"Tech-compatible (mapped): {mapped} ({mapped/total*100:.1f}%)")
        print(f"Not tech-compatible: {unmapped} ({unmapped/total*100:.1f}%)")

        print("\n" + "=" * 80)
        print("BREAKDOWN BY IMPLEMENTATION OBJECTIVE")
        print("=" * 80)

        for io, interventions in results['by_io'].items():
            if not interventions:
                continue

            print(f"\n{io}")
            print("-" * 80)
            print(f"Count: {len(interventions)}")

            # Sort by evidence quality
            interventions.sort(key=lambda x: x['evidence_quality'], reverse=True)

            print(f"\nTop 5 by Evidence Quality:")
            for i, interv in enumerate(interventions[:5], 1):
                print(f"  {i}. {interv['intervention_name']}")
                print(f"     Evidence: {interv['evidence_quality']:.1f}, "
                      f"Validity: {interv['external_validity']:.1f}, "
                      f"Studies: {interv['num_studies']}")

        print("\n" + "=" * 80)
        print("SAMPLE UNMAPPED INTERVENTIONS")
        print("=" * 80)
        print("\nThese don't appear to be tech-compatible based on keywords:")
        for i, interv in enumerate(results['unmapped'][:10], 1):
            print(f"{i}. {interv['intervention_name']}")

    def save_mapped(self, results: dict, output_file: str):
        """Save only the mapped (tech-compatible) interventions."""
        with open(output_file, 'w') as f:
            json.dump(results['mapped'], f, indent=2)
        print(f"\n✅ Saved {len(results['mapped'])} tech-compatible interventions to {output_file}")


def manual_overrides(intervention: dict) -> Optional[str]:
    """
    Manual overrides for specific interventions that need special handling.
    Returns IO name or None to use automatic mapping.
    """
    name = intervention['intervention_name'].lower()

    # Explicitly tech interventions
    if any(term in name for term in ['intelligent tutoring', 'itss', 'technology enhanced', 'teemss',
                                      'computer', 'software', 'digital', 'online', 'web-based',
                                      'read 180', 'accelerated reader', 'accelerated math']):
        return IOS['tutoring']

    # Social-emotional interventions often have tech components
    if any(term in name for term in ['social belonging', 'mindset', 'belonging', 'self-affirmation']):
        return IOS['personalized']

    # Teacher certification/effectiveness - data-driven decision making
    if any(term in name for term in ['teach for america', 'tfa', 'teaching fellows', 'teacher residency']):
        return IOS['decision']

    # Well-known comprehensive programs that are tech-enabled
    if any(term in name for term in ['linked learning', 'first year experience', 'fye']):
        return IOS['mobility']

    # Math/reading programs that could be tech-enabled
    if any(term in name for term in ['scott foresman', 'addison wesley', 'passport reading',
                                      'xtreme reading', 'read naturally', 'building blocks']):
        return IOS['tutoring']

    # Summer bridge and transition programs
    if 'summer bridge' in name:
        return IOS['mobility']

    return None


def main():
    """Main mapping pipeline."""
    mapper = WWCtoIOMapper('/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/research_assistant/wwc_level3_metrics.json')

    # Apply manual overrides first
    for intervention in mapper.interventions:
        override = manual_overrides(intervention)
        if override:
            intervention['_manual_override'] = override

    # Map all interventions
    results = mapper.map_all()

    # Generate report
    mapper.generate_report(results)

    # Save mapped interventions
    mapper.save_mapped(results, '/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/research_assistant/wwc_level3_mapped.json')

    # Save full results with stats
    with open('/Users/alymoosa/Documents/A-Moosa-Dev/AI-EDU-Dev/research_assistant/wwc_mapping_results.json', 'w') as f:
        json.dump({
            'total': len(mapper.interventions),
            'mapped_count': len(results['mapped']),
            'unmapped_count': len(results['unmapped']),
            'by_io_counts': {io: len(intervs) for io, intervs in results['by_io'].items()},
            'unmapped_sample': [i['intervention_name'] for i in results['unmapped'][:20]]
        }, f, indent=2)

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review the mapping above")
    print("2. If satisfied, proceed to import into Neo4j")
    print("3. If not, adjust MAPPING_RULES or manual_overrides() and re-run")


if __name__ == "__main__":
    main()

"""Service for computing visualization data."""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add research_assistant to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.neo4j_config import get_neo4j_connection, OUTCOMES, IMPLEMENTATION_OBJECTIVES


class VisualizationService:
    """Compute data for Level 1 and Level 2 visualizations."""

    def __init__(self):
        self.conn = get_neo4j_connection()
        self.driver = self.conn.connect()

    # ========== LEVEL 1: PROBLEM BURDEN MAP ==========

    def get_level1_data(self) -> Dict[str, Any]:
        """
        Get data for Level 1: Problem Burden Map.
        Returns 12 bubbles (one per outcome).
        """
        bubbles = []

        for outcome in OUTCOMES:
            bubble = self._compute_outcome_bubble(outcome)
            bubbles.append(bubble)

        # Calculate median problem burden for priority classification
        burden_values = [b['y'] for b in bubbles if b['y'] > 0]
        median_burden = self._calculate_median(burden_values) if burden_values else 1.0

        # Update each bubble with priority tag based on median
        for bubble in bubbles:
            bubble['priority'] = self._calculate_priority_level1(
                bubble['x'],
                bubble['y'],
                median_burden
            )

        metadata = {
            "x_axis": {
                "label": "Evidence Maturity",
                "description": "How well-understood this problem is (0-100 composite score)",
                "computation": "4-component composite score (25 points each): Design Strength (RCT = 25, Meta-analysis = 20, Quasi-exp = 15, Correlational = 10, Case study = 5), Consistency (% of papers with same directional finding), External Validity (diversity of regions, school types, populations), and Quality (inverted evidence_type_strength where 0 = highest quality)"
            },
            "y_axis": {
                "label": "Problem Burden Scale",
                "description": "Scope of impact (1 = localized, 4 = systemic)",
                "computation": "Weighted average of user_type across all papers: Student/Educator/Administrator/Parent = 1 (localized), School = 2 (institutional), Community = 3 (regional), Systemic = 4 (policy-level)",
                "median": median_burden
            },
            "bubble_size": {
                "label": "Effort Required",
                "description": "Effort to meaningfully shift this problem",
                "computation": "Sum of two components: System Impact Levels (0 = classroom only, 4 = cross-sector impact) + Decision Making Complexity (0 = one actor, 4 = 10+ actors involved)"
            }
        }

        return {"bubbles": bubbles, "metadata": metadata}

    def _compute_outcome_bubble(self, outcome: str) -> Dict[str, Any]:
        """Compute single bubble for an outcome."""

        # Get all papers targeting this outcome
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
                WHERE out.name = $outcome OR out.type = $outcome
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
                RETURN
                    p.title as title,
                    p.study_design as study_design,
                    p.year as year,
                    p.population as population,
                    p.user_type as user_type,
                    p.url as url,
                    f.direction as direction,
                    f.evidence_type_strength as evidence_type_strength,
                    f.system_impact_levels as system_impact_levels,
                    f.decision_making_complexity as decision_making_complexity,
                    f.region as region,
                    f.school_type as school_type
            """, outcome=outcome)

            papers = [dict(record) for record in result]

        if not papers:
            # No papers for this outcome
            return {
                "id": outcome,
                "label": outcome,
                "x": 0,
                "y": 0,
                "size": 0,
                "paper_count": 0,
                "breakdown": {}
            }

        # X-axis: Evidence Maturity (0-100)
        evidence_maturity = self._compute_evidence_maturity(papers, outcome)

        # Y-axis: Problem Burden Scale (weighted average of user_type)
        problem_scale = self._compute_problem_scale(papers)

        # Bubble Size: Average of system_impact_levels + decision_making_complexity
        bubble_size = self._compute_bubble_size_level1(papers)

        # Breakdown for click interaction
        avg_system = self._safe_avg([p.get('system_impact_levels') for p in papers if p.get('system_impact_levels') is not None and p.get('system_impact_levels') >= 0])
        avg_decision = self._safe_avg([p.get('decision_making_complexity') for p in papers if p.get('decision_making_complexity') is not None and p.get('decision_making_complexity') >= 0])

        breakdown = {
            "evidence_maturity": {
                "score": evidence_maturity,
                "max": 100,
                "description": "How well-understood this problem is",
                "components": self._get_evidence_maturity_breakdown(papers, outcome)
            },
            "problem_scale": {
                "score": round(problem_scale, 2),
                "min": 1,
                "max": 4,
                "description": "Scope of impact: 1 = localized (student/teacher), 4 = systemic (policy-level)",
                "distribution": self._get_user_type_distribution(papers)
            },
            "effort_required": {
                "score": round(bubble_size, 2),
                "description": "Effort to meaningfully shift this problem",
                "components": {
                    "system_impact": {
                        "score": round(avg_system, 2),
                        "description": "Levels of system affected (0 = classroom to 4 = cross-sector)"
                    },
                    "decision_complexity": {
                        "score": round(avg_decision, 2),
                        "description": "Number of decision-makers involved (0 = one actor to 4 = >10 actors)"
                    }
                }
            }
        }

        # Priority will be calculated in get_level1_data after median is computed
        return {
            "id": outcome,
            "label": outcome,
            "x": evidence_maturity,
            "y": problem_scale,
            "size": bubble_size,
            "paper_count": len(papers),
            "priority": "research_gap",  # Temporary, will be updated with actual priority
            "breakdown": breakdown
        }

    def _compute_problem_scale(self, papers: List[Dict]) -> float:
        """
        Compute Y-axis: Problem Burden Scale.
        Weighted average of user_type:
        - Student, Educator, Administrator, Parent = 1 (localized)
        - School = 2 (institutional)
        - Community = 3 (systemic)
        - Systemic = 4 (most systemic)
        """
        user_type_weights = {
            "Student": 1,
            "Educator": 1,
            "Administrator": 1,
            "Parent": 1,
            "School": 2,
            "Community": 3,
            "Systemic": 4,
            "Systematic: social/political level information": 4  # Full string from DB
        }

        weighted_sum = 0
        total_count = 0

        for paper in papers:
            user_type = paper.get('user_type', '')
            if user_type in user_type_weights:
                weighted_sum += user_type_weights[user_type]
                total_count += 1

        if total_count == 0:
            return 1.0  # Default to localized

        return weighted_sum / total_count

    def _compute_bubble_size_level1(self, papers: List[Dict]) -> float:
        """
        Compute bubble size for Level 1.
        Average of system_impact_levels + decision_making_complexity.
        """
        system_impacts = [p.get('system_impact_levels') for p in papers if p.get('system_impact_levels') is not None and p.get('system_impact_levels') >= 0]
        decision_complexities = [p.get('decision_making_complexity') for p in papers if p.get('decision_making_complexity') is not None and p.get('decision_making_complexity') >= 0]

        avg_system = self._safe_avg(system_impacts)
        avg_decision = self._safe_avg(decision_complexities)

        return avg_system + avg_decision

    def _get_user_type_distribution(self, papers: List[Dict]) -> Dict[str, int]:
        """Get count of papers by user_type."""
        distribution = {}
        for paper in papers:
            user_type = paper.get('user_type', 'not_reported')
            distribution[user_type] = distribution.get(user_type, 0) + 1
        return distribution

    # ========== LEVEL 2: INTERVENTION EVIDENCE MAP ==========

    def get_level2_data(self) -> Dict[str, Any]:
        """
        Get data for Level 2: Intervention Evidence Map.
        Returns 4 bubbles (one per Implementation Objective).
        """
        bubbles = []

        # Investment amounts per IO (USP investments in AI, last updated: 1/12/2026)
        investments = {
            "Intelligent Tutoring and Instruction": 315045557,
            "AI-Enable Personalized Advising": 74753110,  # Note: matches DB typo "Enable" not "Enabled"
            "Institutional Decision-making": 584493624,  # Note: lowercase 'm' to match DB
            "AI-Enabled Learner Mobility": 199803225
        }

        for io in IMPLEMENTATION_OBJECTIVES:
            bubble = self._compute_io_bubble(io, investments.get(io, 0))
            bubbles.append(bubble)

        # Calculate median potential impact for priority classification
        impact_values = [b['y'] for b in bubbles if b['y'] > 0]
        median_impact = self._calculate_median(impact_values) if impact_values else 0

        # Update each bubble with priority tag
        for bubble in bubbles:
            bubble['priority'] = self._calculate_priority_level2(
                bubble['x'],
                bubble['y'],
                median_impact
            )

        metadata = {
            "x_axis": {
                "label": "Evidence Maturity",
                "description": "Quality and reliability of intervention evidence (0-100)",
                "computation": "Same 4-component composite as Level 1: Design Strength (RCT = 25, Meta-analysis = 20, etc.), Consistency (directional stability across studies), External Validity (diversity of settings/populations), and Quality (risk of bias)"
            },
            "y_axis": {
                "label": "Potential Impact",
                "description": "Alignment to high-burden problems from Level 1",
                "computation": "Sum of Problem Burden Scale (Y-axis) values from Level 1 for all outcomes this intervention targets. Higher value = intervention addresses more urgent/systemic problems",
                "median": median_impact
            },
            "bubble_size": {
                "label": "R&D Investment Required",
                "description": "Investment needed to move pathway to field-ready use",
                "computation": "Sum of two components: Evidence Maturity Gap (4 - evidence_type_strength, so early prototypes = 4, mature evidence = 0) + Evaluation Burden Cost (0 = short-term/simple eval, 4 = long-term/complex eval required)"
            },
            "investments": investments
        }

        return {"bubbles": bubbles, "metadata": metadata}

    def _compute_io_bubble(self, io: str, investment: int) -> Dict[str, Any]:
        """Compute single bubble for an Implementation Objective."""

        # Get all papers with this IO
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE io.type = $io OR io.name = $io
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
                MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
                RETURN
                    p.title as title,
                    p.study_design as study_design,
                    p.year as year,
                    p.population as population,
                    p.user_type as user_type,
                    p.url as url,
                    f.direction as direction,
                    f.evidence_type_strength as evidence_type_strength,
                    f.evaluation_burden_cost as evaluation_burden_cost,
                    f.system_impact_levels as system_impact_levels,
                    f.decision_making_complexity as decision_making_complexity,
                    f.region as region,
                    f.school_type as school_type,
                    out.name as outcome,
                    out.type as outcome_type
            """, io=io)

            papers = [dict(record) for record in result]

        if not papers:
            return {
                "id": io,
                "label": io,
                "x": 0,
                "y": 0,
                "size": 0,
                "paper_count": 0,
                "breakdown": {"investment": investment}
            }

        # X-axis: Evidence Maturity (same as Level 1)
        evidence_maturity = self._compute_evidence_maturity(papers, io)

        # Y-axis: Potential Impact (sum of burden weights from Level 1)
        potential_impact = self._compute_potential_impact(io)

        # Bubble Size: Average of inverted evidence_type_strength + evaluation_burden_cost
        bubble_size = self._compute_bubble_size_level2(papers)

        # Breakdown for click interaction
        avg_evidence_strength = self._safe_avg([4 - p.get('evidence_type_strength', 4) for p in papers if p.get('evidence_type_strength') is not None and p.get('evidence_type_strength') >= 0])
        avg_eval_burden = self._safe_avg([p.get('evaluation_burden_cost') for p in papers if p.get('evaluation_burden_cost') is not None and p.get('evaluation_burden_cost') >= 0])

        breakdown = {
            "investment": {
                "amount": investment,
                "formatted": f"${investment:,}",
                "description": "This information was calculated by examining USP's investments in AI across the four implementation objectives. Last updated: 1/12/2026"
            },
            "evidence_maturity": {
                "score": evidence_maturity,
                "max": 100,
                "description": "Quality and reliability of intervention evidence",
                "components": self._get_evidence_maturity_breakdown(papers, io)
            },
            "potential_impact": {
                "score": round(potential_impact, 2),
                "description": "Alignment to high-burden problems (sum of Level 1 burden weights)",
                "outcomes_targeted": list(set([p.get('outcome') or p.get('outcome_type') for p in papers if (p.get('outcome') or p.get('outcome_type'))]))
            },
            "r_and_d_required": {
                "score": round(bubble_size, 2),
                "description": "Additional R&D investment needed to reach field readiness",
                "components": {
                    "evidence_maturity_gap": {
                        "score": round(avg_evidence_strength, 2),
                        "description": "Gap in evidence quality (4 = early prototype, 0 = mature evidence)"
                    },
                    "evaluation_burden": {
                        "score": round(avg_eval_burden, 2),
                        "description": "Cost to rigorously evaluate (0 = short-term/simple, 4 = long-term/complex)"
                    }
                }
            }
        }

        # Priority will be calculated in get_level2_data after median is computed
        return {
            "id": io,
            "label": io,
            "x": evidence_maturity,
            "y": potential_impact,
            "size": bubble_size,
            "paper_count": len(papers),
            "priority": "research_gap",  # Temporary, will be updated with actual priority
            "breakdown": breakdown
        }

    def _compute_potential_impact(self, io: str) -> float:
        """
        Compute Y-axis for Level 2: Potential Impact.
        Sum of problem burden weights from Level 1 for all outcomes this IO targets.
        """
        # Get all outcomes this IO targets
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE io.type = $io OR io.name = $io
                MATCH (p)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
                RETURN DISTINCT out.name as outcome, out.type as outcome_type
            """, io=io)

            targeted_outcomes = [record.get('outcome') or record.get('outcome_type') for record in result]

        # Get Level 1 data to fetch burden weights
        level1_data = self.get_level1_data()
        level1_bubbles = {b['id']: b for b in level1_data['bubbles']}

        # Sum the burden sizes (problem scale * bubble size)
        total_impact = 0
        for outcome in targeted_outcomes:
            if outcome in level1_bubbles:
                bubble = level1_bubbles[outcome]
                # Use Y-axis (problem scale) as the burden weight
                total_impact += bubble['y']

        return total_impact

    def _compute_bubble_size_level2(self, papers: List[Dict]) -> float:
        """
        Compute bubble size for Level 2: R&D Investment Required.
        Average of:
        - Inverted evidence_type_strength (4 - score, so 0 becomes 4, 4 becomes 0)
        - evaluation_burden_cost (0-4 scale)
        Higher cost = bigger bubble.
        """
        inverted_evidence = [4 - p.get('evidence_type_strength', 4) for p in papers if p.get('evidence_type_strength') is not None and p.get('evidence_type_strength') >= 0]
        eval_burdens = [p.get('evaluation_burden_cost') for p in papers if p.get('evaluation_burden_cost') is not None and p.get('evaluation_burden_cost') >= 0]

        avg_evidence = self._safe_avg(inverted_evidence)
        avg_burden = self._safe_avg(eval_burdens)

        return avg_evidence + avg_burden

    # ========== EVIDENCE MATURITY CALCULATION (SHARED) ==========

    def _compute_evidence_maturity(self, papers: List[Dict], entity_name: str) -> float:
        """
        Compute evidence maturity score (0-100) based on:
        1. Design strength (25 points)
        2. Consistency (25 points)
        3. External validity (25 points)
        4. Bias/quality (25 points)
        """
        design_score = self._compute_design_strength(papers)
        consistency_score = self._compute_consistency(papers)
        validity_score = self._compute_external_validity(papers)
        quality_score = self._compute_quality_score(papers)

        total = design_score + consistency_score + validity_score + quality_score
        return round(total, 2)

    def _compute_design_strength(self, papers: List[Dict]) -> float:
        """
        Design strength component (0-25 points).
        Weight by study design hierarchy: RCT (highest), then meta-analysis, then quasi-experimental, etc.
        """
        design_weights = {
            'Randomized Control Trial': 25,
            'Meta-Analysis/Systematic Review': 20,
            'Quasi-Experimental Design': 15,
            'Correlational': 10,
            'Case Study': 5,
            'not_reported': 0
        }

        total_weight = 0
        count = 0

        for paper in papers:
            design = paper.get('study_design', 'not_reported')
            # Try direct match first
            if design in design_weights:
                total_weight += design_weights[design]
                count += 1
            # Fallback: case-insensitive partial matching
            else:
                design_lower = str(design).lower() if design else ''
                if 'randomized' in design_lower or 'rct' in design_lower:
                    total_weight += 25
                    count += 1
                elif 'meta-analysis' in design_lower or 'systematic review' in design_lower:
                    total_weight += 20
                    count += 1
                elif 'quasi' in design_lower:
                    total_weight += 15
                    count += 1
                elif 'correlational' in design_lower:
                    total_weight += 10
                    count += 1
                elif 'case' in design_lower:
                    total_weight += 5
                    count += 1

        return (total_weight / count) if count > 0 else 0

    def _compute_consistency(self, papers: List[Dict]) -> float:
        """
        Consistency component (0-25 points).
        Are findings directionally stable?
        """
        directions = [p.get('direction', '') for p in papers if p.get('direction')]

        if not directions:
            return 0

        # Count each direction
        positive = directions.count('Positive')
        negative = directions.count('Negative')
        mixed = directions.count('Mixed')
        no_effect = directions.count('No Effect')

        total = len(directions)

        # High consistency = one direction dominates
        max_direction = max(positive, negative, mixed, no_effect)
        consistency_ratio = max_direction / total

        return consistency_ratio * 25

    def _compute_external_validity(self, papers: List[Dict]) -> float:
        """
        External validity component (0-25 points).
        Diversity of settings and populations.
        """
        unique_regions = len(set([p.get('region', '') for p in papers if p.get('region')]))
        unique_school_types = len(set([p.get('school_type', '') for p in papers if p.get('school_type')]))
        unique_populations = len(set([p.get('population', '') for p in papers if p.get('population')]))

        # More diversity = higher score
        # Cap at 5 unique values per dimension
        diversity_score = (
            min(unique_regions, 5) / 5 * 10 +
            min(unique_school_types, 5) / 5 * 7.5 +
            min(unique_populations, 5) / 5 * 7.5
        )

        return diversity_score

    def _compute_quality_score(self, papers: List[Dict]) -> float:
        """
        Quality/bias component (0-25 points).
        Based on evidence_type_strength (0 is best, 4 is worst).
        """
        strengths = [p.get('evidence_type_strength') for p in papers if p.get('evidence_type_strength') is not None and p.get('evidence_type_strength') >= 0]

        if not strengths:
            return 0

        # Invert scale: 0 -> 25 points, 4 -> 0 points
        avg_strength = sum(strengths) / len(strengths)
        inverted = 4 - avg_strength

        return (inverted / 4) * 25

    def _get_evidence_maturity_breakdown(self, papers: List[Dict], entity_name: str) -> Dict[str, Any]:
        """Get detailed breakdown of evidence maturity components with descriptions."""
        design_score = self._compute_design_strength(papers)
        consistency_score = self._compute_consistency(papers)
        validity_score = self._compute_external_validity(papers)
        quality_score = self._compute_quality_score(papers)

        return {
            "design_strength": {
                "score": round(design_score, 2),
                "max": 25,
                "description": "Study design quality (RCT highest, then meta-analysis, quasi-experimental, correlational, case study)"
            },
            "consistency": {
                "score": round(consistency_score, 2),
                "max": 25,
                "description": "Directional stability of findings across studies"
            },
            "external_validity": {
                "score": round(validity_score, 2),
                "max": 25,
                "description": "Diversity of settings, regions, and populations studied"
            },
            "quality": {
                "score": round(quality_score, 2),
                "max": 25,
                "description": "Risk of bias and methodological rigor"
            }
        }

    # ========== PRIORITY CALCULATION METHODS ==========

    def _calculate_priority_level1(self, evidence_maturity: float, problem_scale: float, median_burden: float) -> str:
        """
        Calculate priority tag for Level 1 bubbles.

        Logic:
        - High Priority: x > 65 AND y > median (well-understood systemic problems)
        - On Watch: (x <= 65 AND y > median) OR (x > 65 AND y <= median) - either high burden with low evidence OR high evidence with low burden
        - Research Gap: x <= 65 AND y <= median (low evidence and low burden)
        """
        EVIDENCE_THRESHOLD = 65

        if evidence_maturity > EVIDENCE_THRESHOLD and problem_scale > median_burden:
            return "high_priority"
        elif (evidence_maturity <= EVIDENCE_THRESHOLD and problem_scale > median_burden) or \
             (evidence_maturity > EVIDENCE_THRESHOLD and problem_scale <= median_burden):
            return "on_watch"
        else:
            return "research_gap"

    def _calculate_priority_level2(self, evidence_maturity: float, potential_impact: float, median_impact: float) -> str:
        """
        Calculate priority tag for Level 2 bubbles.

        Logic:
        - High Priority: x > 65 AND y > median (proven interventions for urgent problems)
        - On Watch: x <= 65 AND y > median (promising but need validation)
        - Research Gap: y <= median (narrow scope or insufficient evidence)
        """
        EVIDENCE_THRESHOLD = 65

        if evidence_maturity > EVIDENCE_THRESHOLD and potential_impact > median_impact:
            return "high_priority"
        elif evidence_maturity <= EVIDENCE_THRESHOLD and potential_impact > median_impact:
            return "on_watch"
        else:
            return "research_gap"

    # ========== UTILITY METHODS ==========

    def _calculate_median(self, values: List[float]) -> float:
        """Calculate proper median (handles even and odd number of values)."""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            # Even number: average of two middle values
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            # Odd number: middle value
            return sorted_values[n // 2]

    def _safe_avg(self, values: List[float]) -> float:
        """Safely compute average, return 0 if empty."""
        if not values:
            return 0
        return sum(values) / len(values)

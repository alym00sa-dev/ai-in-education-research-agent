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
            },
            "study_design_distribution": self._get_study_design_distribution(papers)
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

    def _get_study_design_distribution(self, papers: List[Dict]) -> Dict[str, int]:
        """Get count of papers by study_design."""
        distribution = {}
        for paper in papers:
            study_design = paper.get('study_design', 'not_reported')
            if study_design:
                distribution[study_design] = distribution.get(study_design, 0) + 1
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
            },
            "study_design_distribution": self._get_study_design_distribution(papers)
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

    # ========== LEVEL 3: EVIDENCE-BASED INTERVENTIONS MAP (WWC DATA) ==========

    def get_level3_data(self) -> Dict[str, Any]:
        """
        Get data for Level 3: Evidence-Based Interventions Map (WWC data).
        Returns bubbles for each broadened Implementation Objective with WWC evidence.
        """
        # Broadened IOs for Level 3 (tech-compatible, not just AI)
        BROADENED_IOS = [
            "Adaptive Instruction & Tutoring Systems",
            "Personalized Learning & Advising Systems",
            "Data-Driven Decision Support",
            "Learning Pathways & Mobility Support"
        ]

        bubbles = []

        for io in BROADENED_IOS:
            bubble = self._compute_io_bubble_level3(io)
            bubbles.append(bubble)

        # Calculate median external validity for priority classification
        validity_values = [b['y'] for b in bubbles if b['y'] > 0]
        median_validity = self._calculate_median(validity_values) if validity_values else 0

        # Update each bubble with priority tag
        for bubble in bubbles:
            bubble['priority'] = self._calculate_priority_level3(
                bubble['x'],
                bubble['y'],
                median_validity
            )

        metadata = {
            "x_axis": {
                "label": "Evidence Base Quality",
                "description": "Rigor and consistency of RCT evidence (0-100)",
                "computation": "4-component composite: Study Design Quality (WWC ratings), Replication Strength (number of studies), Sample Adequacy (total students), and Effect Consistency (stability across findings)"
            },
            "y_axis": {
                "label": "External Validity Score",
                "description": "Generalizability across diverse contexts",
                "computation": "Diversity across geographic regions, school types, demographics (ELL, FRPL, race), grade levels, and urbanicity. Higher score indicates findings replicate across more contexts.",
                "median": median_validity
            },
            "bubble_size": {
                "label": "Students Impacted",
                "description": "Scale of evidence (studies × sample size)",
                "computation": "Number of rigorous studies meeting WWC standards multiplied by average sample size. Represents total students already impacted by this intervention."
            }
        }

        return {"bubbles": bubbles, "metadata": metadata}

    def _compute_io_bubble_level3(self, io: str) -> Dict[str, Any]:
        """Compute single bubble for an Implementation Objective using WWC data."""

        # Get all WWC papers with this IO
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE io.type = $io OR io.name = $io
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                RETURN
                    p.title as title,
                    p.study_design as study_design,
                    p.year as year,
                    p.population as population,
                    p.user_type as user_type,
                    p.url as url,
                    p.wwc_study_rating as wwc_study_rating,
                    f.direction as direction,
                    f.evidence_type_strength as evidence_type_strength,
                    f.study_size as study_size,
                    f.effect_size as effect_size,
                    f.region as region,
                    f.school_type as school_type,
                    f.wwc_is_significant as wwc_is_significant
            """, io=io)

            papers = [dict(record) for record in result]

        if not papers:
            # No WWC papers for this IO
            return {
                "id": io,
                "label": io,
                "x": 0,
                "y": 0,
                "size": 0,
                "paper_count": 0,
                "breakdown": {}
            }

        # X-axis: Evidence Base Quality (0-100)
        evidence_quality = self._compute_evidence_quality_wwc(papers)

        # Y-axis: External Validity Score
        external_validity = self._compute_external_validity_wwc(papers)

        # Bubble Size: Studies × Average Sample Size
        bubble_size = self._compute_bubble_size_level3(papers)

        # Breakdown for click interaction
        breakdown = self._calculate_breakdown_level3(io, papers)

        # Priority will be calculated in get_level3_data after median is computed
        return {
            "id": io,
            "label": io,
            "x": evidence_quality,
            "y": external_validity,
            "size": bubble_size,
            "paper_count": len(set(p['title'] for p in papers)),
            "priority": "research_gap",  # Temporary, will be updated
            "breakdown": breakdown
        }

    def _compute_evidence_quality_wwc(self, papers: List[Dict]) -> float:
        """
        Compute Evidence Base Quality for WWC data (0-100).

        Components:
        1. Study Design Quality (25 pts) - WWC ratings
        2. Replication Strength (25 pts) - Number of unique studies
        3. Sample Adequacy (25 pts) - Total sample sizes
        4. Effect Consistency (25 pts) - Consistency of effects
        """
        if not papers:
            return 0.0

        # 1. Study Design Quality (25 pts) based on WWC ratings
        rating_scores = {
            'Meets WWC standards without reservations': 25,
            'Meets WWC standards with reservations': 15,
            'Does not meet WWC standards': 5,
            'Ineligible for review': 0
        }

        ratings = [rating_scores.get(p.get('wwc_study_rating', ''), 10) for p in papers]
        design_quality = self._safe_avg(ratings)

        # 2. Replication Strength (25 pts) - based on number of unique studies
        unique_studies = len(set(p['title'] for p in papers))
        if unique_studies >= 10:
            replication_score = 25
        elif unique_studies >= 7:
            replication_score = 22
        elif unique_studies >= 5:
            replication_score = 20
        elif unique_studies >= 3:
            replication_score = 15
        elif unique_studies >= 2:
            replication_score = 10
        else:
            replication_score = 5

        # 3. Sample Adequacy (25 pts)
        total_sample = sum(p.get('study_size', 0) for p in papers if p.get('study_size'))
        # Normalize: 1000+ students = 25 pts
        sample_score = min(25, (total_sample / 1000) * 25) if total_sample else 0

        # 4. Effect Consistency (25 pts)
        effect_sizes = [p.get('effect_size') for p in papers
                       if p.get('effect_size') is not None]

        if len(effect_sizes) > 1:
            import statistics
            std_dev = statistics.stdev(effect_sizes)
            # Lower std dev = more consistent = higher score
            # Std dev of 0.3 or less = full 25 pts
            consistency_score = max(0, 25 - (std_dev * 83))  # 1/0.012 ≈ 83
        elif len(effect_sizes) == 1:
            consistency_score = 15
        else:
            consistency_score = 0

        total = design_quality + replication_score + sample_score + consistency_score
        return round(total, 2)

    def _compute_external_validity_wwc(self, papers: List[Dict]) -> float:
        """
        Compute External Validity Score for WWC data.

        Measures diversity across:
        - Geographic regions
        - School types
        - Grade levels (population)
        - Urbanicity (inferred from school_type)
        """
        if not papers:
            return 0.0

        # Collect unique values
        unique_regions = len(set(p.get('region', '') for p in papers
                                if p.get('region') and p.get('region') != 'not_reported'))
        unique_school_types = len(set(p.get('school_type', '') for p in papers
                                     if p.get('school_type') and p.get('school_type') != 'not_reported'))
        unique_populations = len(set(p.get('population', '') for p in papers
                                    if p.get('population') and p.get('population') != 'not_reported'))

        # Calculate score components (out of 50 total)
        region_score = min(20, unique_regions * 2)  # Max 20 pts (10 regions)
        school_type_score = min(15, unique_school_types * 5)  # Max 15 pts (3 types)
        population_score = min(15, unique_populations * 3)  # Max 15 pts (5 pops)

        total = region_score + school_type_score + population_score
        return round(total, 2)

    def _compute_bubble_size_level3(self, papers: List[Dict]) -> float:
        """
        Compute bubble size for Level 3: Studies × Average Sample Size.
        """
        unique_studies = len(set(p['title'] for p in papers))
        total_sample = sum(p.get('study_size', 0) for p in papers if p.get('study_size'))
        avg_sample = total_sample / len(papers) if papers else 0

        size = unique_studies * avg_sample
        return round(size, 2)

    def _calculate_breakdown_level3(self, io: str, papers: List[Dict]) -> Dict[str, Any]:
        """Calculate detailed breakdown data for Level 3 popup."""

        # Effect sizes
        effect_sizes = [p.get('effect_size') for p in papers
                       if p.get('effect_size') is not None]
        avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

        # Unique studies
        unique_studies = len(set(p['title'] for p in papers))

        # Total sample
        total_sample = sum(p.get('study_size', 0) for p in papers if p.get('study_size'))

        # Statistical significance rate
        sig_findings = sum(1 for p in papers if p.get('wwc_is_significant'))
        sig_rate = (sig_findings / len(papers) * 100) if papers else 0

        # Study ratings distribution
        ratings = {}
        for p in papers:
            rating = p.get('wwc_study_rating', 'not_reported')
            ratings[rating] = ratings.get(rating, 0) + 1

        # Regions covered
        regions = list(set(p.get('region', '') for p in papers
                          if p.get('region') and p.get('region') != 'not_reported'))

        return {
            "evidence_quality": {
                "score": self._compute_evidence_quality_wwc(papers),
                "max": 100,
                "description": "Rigor and replication of RCT evidence from What Works Clearinghouse"
            },
            "external_validity": {
                "score": self._compute_external_validity_wwc(papers),
                "max": 50,
                "description": "Generalizability across regions, school types, and grade levels"
            },
            "students_impacted": {
                "total": total_sample,
                "studies": unique_studies,
                "avg_per_study": round(total_sample / unique_studies) if unique_studies else 0,
                "description": "Total students studied across all RCTs"
            },
            "effect_summary": {
                "average_effect_size": round(avg_effect, 3),
                "num_findings": len(papers),
                "significant_rate": round(sig_rate, 1),
                "description": "Average effect size from WWC meta-analysis"
            },
            "wwc_ratings": ratings,
            "regions_covered": regions,
            "study_design_distribution": self._get_study_design_distribution(papers)
        }

    def _calculate_priority_level3(self, evidence_quality: float, external_validity: float,
                                   median_validity: float) -> str:
        """
        Calculate priority tag for Level 3 bubbles.

        Logic:
        - High Priority: x > 70 AND y > median (strong evidence + highly generalizable)
        - On Watch: x > 70 AND y <= median (strong evidence but limited contexts)
        - Research Gap: x <= 70 (needs more rigorous replication)
        """
        EVIDENCE_THRESHOLD = 70

        if evidence_quality > EVIDENCE_THRESHOLD and external_validity > median_validity:
            return "high_priority"
        elif evidence_quality > EVIDENCE_THRESHOLD and external_validity <= median_validity:
            return "on_watch"
        else:
            return "research_gap"

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

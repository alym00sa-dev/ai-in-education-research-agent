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

        # Get all papers targeting this outcome (excluding WWC papers)
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)-[:FOCUSES_ON_OUTCOME]->(out:Outcome)
                WHERE (out.name = $outcome OR out.type = $outcome)
                  AND (p.source IS NULL OR p.source <> 'WWC')
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

        # Get all papers with this IO (excluding WWC papers)
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND (p.source IS NULL OR p.source <> 'WWC')
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

        # Unique colors for each bubble (no semantic meaning)
        BUBBLE_COLORS = [
            "#3b82f6",  # Blue
            "#10b981",  # Green
            "#f59e0b",  # Amber
            "#8b5cf6"   # Purple
        ]

        bubbles = []

        for i, io in enumerate(BROADENED_IOS):
            bubble = self._compute_io_bubble_level3(io)
            bubble['color'] = BUBBLE_COLORS[i]
            bubble['priority'] = 'neutral'  # No priority classification for Level 3
            bubbles.append(bubble)

        metadata = {
            "x_axis": {
                "label": "Evidence Base Quality",
                "description": "Rigor and consistency of RCT evidence (0-100, RCTs only)",
                "computation": "4-component composite: Study Design Quality (WWC ratings), Replication Strength (number of RCT studies), Sample Adequacy (total students in RCTs), and Effect Consistency (stability across findings). Only includes randomized controlled trials, not quasi-experimental designs."
            },
            "y_axis": {
                "label": "External Validity Score",
                "description": "Generalizability across diverse contexts",
                "computation": "Diversity across geographic regions, school types, demographics (ELL, FRPL, race), grade levels, and urbanicity. Higher score indicates findings replicate across more contexts."
            },
            "bubble_size": {
                "label": "Students Impacted",
                "description": "Total unique students studied across all randomized controlled trials",
                "computation": "Sum of unique students across all RCT studies only (excludes quasi-experimental designs). For each study, we use the maximum sample size to avoid double-counting students across multiple outcome measures. Represents actual scale of rigorous experimental testing."
            }
        }

        return {"bubbles": bubbles, "metadata": metadata}

    def _compute_io_bubble_level3(self, io: str) -> Dict[str, Any]:
        """Compute single bubble for an Implementation Objective using WWC data."""

        # Get all WWC papers with this IO - ONLY RCTs (exclude quasi-experimental designs)
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND p.study_design =~ '(?i).*randomized.*'
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
            # Linear scale: std_dev 0.0 = 25 pts, std_dev 0.6+ = 0 pts
            consistency_score = max(0, 25 * (1 - std_dev / 0.6))
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
        Compute bubble size for Level 3: Total students across unique studies.
        """
        # Group by study and take max study_size per study
        study_samples = {}
        for p in papers:
            title = p.get('title')
            size = p.get('study_size', 0)
            if title and size:
                if title not in study_samples or size > study_samples[title]:
                    study_samples[title] = size

        total_sample = sum(study_samples.values())
        return round(total_sample, 2)

    def _calculate_breakdown_level3(self, io: str, papers: List[Dict]) -> Dict[str, Any]:
        """Calculate detailed breakdown data for Level 3 popup."""

        # Effect sizes
        effect_sizes = [p.get('effect_size') for p in papers
                       if p.get('effect_size') is not None]
        avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

        # Unique studies
        unique_studies = len(set(p['title'] for p in papers))

        # Total sample - group by study and take max study_size per study
        study_samples = {}
        for p in papers:
            title = p.get('title')
            size = p.get('study_size', 0)
            if title and size:
                if title not in study_samples or size > study_samples[title]:
                    study_samples[title] = size
        total_sample = sum(study_samples.values())

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

        # Calculate component scores for evidence quality breakdown
        # 1. Study Design Quality
        rating_scores = {
            'Meets WWC standards without reservations': 25,
            'Meets WWC standards with reservations': 15,
            'Does not meet WWC standards': 5,
            'Ineligible for review': 0
        }
        ratings_list = [rating_scores.get(p.get('wwc_study_rating', ''), 10) for p in papers]
        design_quality = self._safe_avg(ratings_list)

        # 2. Replication Strength
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

        # 3. Sample Adequacy
        sample_score = min(25, (total_sample / 1000) * 25) if total_sample else 0

        # 4. Effect Consistency
        if len(effect_sizes) > 1:
            import statistics
            std_dev = statistics.stdev(effect_sizes)
            # Linear scale: std_dev 0.0 = 25 pts, std_dev 0.75+ = 0 pts
            consistency_score = max(0, 25 * (1 - std_dev / 0.75))
        elif len(effect_sizes) == 1:
            consistency_score = 15
        else:
            consistency_score = 0

        return {
            "evidence_maturity": {
                "score": self._compute_evidence_quality_wwc(papers),
                "max": 100,
                "description": "Rigor and replication of RCT evidence from What Works Clearinghouse",
                "components": {
                    "study_design_quality": {
                        "score": round(design_quality, 2),
                        "max": 25,
                        "description": "WWC study ratings (Meets standards without/with reservations)"
                    },
                    "replication_strength": {
                        "score": round(replication_score, 2),
                        "max": 25,
                        "description": f"Number of independent RCT replications ({unique_studies} studies)"
                    },
                    "sample_adequacy": {
                        "score": round(sample_score, 2),
                        "max": 25,
                        "description": f"Total students studied ({total_sample:,} across all RCTs)"
                    },
                    "effect_consistency": {
                        "score": round(consistency_score, 2),
                        "max": 25,
                        "description": "Stability of effect sizes across studies (lower variance = higher score)"
                    }
                }
            },
            "external_validity": {
                "score": self._compute_external_validity_wwc(papers),
                "max": 50,
                "description": "Generalizability across diverse contexts",
                "regions_covered": regions
            },
            "students_impacted": {
                "score": total_sample,
                "description": "Total students studied across all RCTs",
                "components": {
                    "total_students": {
                        "score": total_sample,
                        "description": f"{total_sample:,} students across {unique_studies} studies"
                    },
                    "avg_per_study": {
                        "score": round(total_sample / unique_studies) if unique_studies else 0,
                        "description": "Average sample size per study"
                    }
                }
            },
            "effect_summary": {
                "average_effect_size": round(avg_effect, 3),
                "num_findings": len(papers),
                "significant_rate": round(sig_rate, 1),
                "description": "Average effect size from WWC studies (Cohen's d)"
            },
            "wwc_ratings": ratings,
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

    # ========== LEVEL 4: INDIVIDUAL INTERVENTIONS (67 BUBBLES) ==========

    def get_level4_data(self) -> Dict[str, Any]:
        """
        Get data for Level 4: Individual Interventions (WWC data).
        Returns 67 bubbles (one per tech-compatible intervention).
        """
        bubbles = []

        # Colors by IO (to show groupings)
        IO_COLORS = {
            "Adaptive Instruction & Tutoring Systems": "#3b82f6",  # Blue
            "Personalized Learning & Advising Systems": "#10b981",  # Green
            "Data-Driven Decision Support": "#f59e0b",  # Amber
            "Learning Pathways & Mobility Support": "#8b5cf6"  # Purple
        }

        # Get all WWC papers with their interventions
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                RETURN DISTINCT
                    p.title as title,
                    p.wwc_study_id as study_id,
                    io.type as io_type
            """)

            papers_data = [dict(record) for record in result]

        # Group by intervention name (extracted from paper titles or use study metadata)
        # For now, we'll use a mapping from our processed data
        import json
        with open('wwc_level3_mapped.json', 'r') as f:
            mapped_interventions = json.load(f)

        for intervention in mapped_interventions:
            bubble = self._compute_intervention_bubble_level4(intervention, IO_COLORS)
            if bubble['paper_count'] > 0:  # Only include interventions with data
                bubbles.append(bubble)

        metadata = {
            "x_axis": {
                "label": "Evidence Base Quality",
                "description": "Rigor and consistency of RCT evidence (0-100)",
                "computation": "4-component composite: Study Design Quality, Replication Strength, Sample Adequacy, and Effect Consistency"
            },
            "y_axis": {
                "label": "External Validity Score",
                "description": "Generalizability across diverse contexts",
                "computation": "Diversity across geographic regions, school types, grade levels, and demographics"
            },
            "bubble_size": {
                "label": "Students Impacted",
                "description": "Total students studied across all RCTs for this intervention",
                "computation": "Number of studies multiplied by average sample size"
            }
        }

        return {"bubbles": bubbles, "metadata": metadata}

    def _compute_intervention_bubble_level4(self, intervention: Dict, io_colors: Dict) -> Dict[str, Any]:
        """Compute single bubble for an individual intervention."""

        intervention_id = intervention['intervention_id']
        intervention_name = intervention['intervention_name']
        io = intervention['implementation_objective']

        # Get papers for this specific intervention from Neo4j
        # We need to match by intervention name since that's how we can identify them
        with self.driver.session() as session:
            # Get study IDs from CSV mapping
            import csv
            csv_path = '../kg-viz-frontend/level-3/Interventions_Studies_And_Findings.csv'

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                study_ids = [row['s_StudyID'] for row in reader
                           if row['i_InterventionID'] == intervention_id and row['s_StudyID']]

            if not study_ids:
                return {
                    "id": intervention_name,
                    "label": intervention_name,
                    "x": 0,
                    "y": 0,
                    "size": 0,
                    "paper_count": 0,
                    "color": io_colors.get(io, "#94a3b8"),
                    "priority": "neutral",
                    "breakdown": {}
                }

            # Get papers for these study IDs
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                WHERE p.wwc_study_id IN $study_ids
                RETURN
                    p.title as title,
                    p.study_design as study_design,
                    p.year as year,
                    p.population as population,
                    p.wwc_study_rating as wwc_study_rating,
                    f.direction as direction,
                    f.evidence_type_strength as evidence_type_strength,
                    f.study_size as study_size,
                    f.effect_size as effect_size,
                    f.region as region,
                    f.school_type as school_type,
                    f.wwc_is_significant as wwc_is_significant
            """, study_ids=study_ids)

            papers = [dict(record) for record in result]

        if not papers:
            return {
                "id": intervention_name,
                "label": intervention_name,
                "x": 0,
                "y": 0,
                "size": 0,
                "paper_count": 0,
                "color": io_colors.get(io, "#94a3b8"),
                "priority": "neutral",
                "breakdown": {}
            }

        # Calculate metrics (same as Level 3)
        evidence_quality = self._compute_evidence_quality_wwc(papers)
        external_validity = self._compute_external_validity_wwc(papers)
        bubble_size = self._compute_bubble_size_level3(papers)
        breakdown = self._calculate_breakdown_level3(io, papers)

        return {
            "id": intervention_name,
            "label": intervention_name,
            "x": evidence_quality,
            "y": external_validity,
            "size": bubble_size,
            "paper_count": len(set(p['title'] for p in papers)),
            "color": io_colors.get(io, "#94a3b8"),
            "priority": "neutral",
            "breakdown": {
                **breakdown,
                "implementation_objective": io
            }
        }

    # ========== LEVEL 5: EVIDENCE EVOLUTION OVER TIME ==========

    def get_level5_data(self) -> Dict[str, Any]:
        """
        Get data for Level 5: Temporal Evidence Evolution.
        Returns time series data showing how evidence scope/generalizability evolved over time.

        FILTERS:
        - Only technology-relevant studies (would need to be tagged in Neo4j)
        - Only "Meets WWC standards without reservations" (highest quality)
        - 3-year buckets

        Y-AXIS: Generalizability/Scope Expansion (not implementation reach)
        """
        # Broadened IOs for Level 3/4/5
        BROADENED_IOS = [
            "Adaptive Instruction & Tutoring Systems",
            "Personalized Learning & Advising Systems",
            "Data-Driven Decision Support",
            "Learning Pathways & Mobility Support"
        ]

        # Colors for each IO line
        IO_COLORS = {
            "Adaptive Instruction & Tutoring Systems": "#3b82f6",
            "Personalized Learning & Advising Systems": "#10b981",
            "Data-Driven Decision Support": "#f59e0b",
            "Learning Pathways & Mobility Support": "#8b5cf6"
        }

        # Create time series for each IO (aggregated view)
        time_series = []
        for io in BROADENED_IOS:
            series = self._compute_time_series_for_io(io, IO_COLORS[io])
            time_series.append(series)

        # Also get individual intervention data for drill-down views
        individual_interventions = {}
        for io in BROADENED_IOS:
            individual_interventions[io] = self._get_individual_interventions_for_io(io, IO_COLORS[io])

        metadata = {
            "x_axis": {
                "label": "Year",
                "description": "Publication year (3-year buckets)",
                "computation": "Studies grouped by publication year into 3-year bins (2000-2002, 2003-2005, etc.)"
            },
            "y_axis": {
                "label": "Generalizability Score",
                "description": "Scope expansion across diverse contexts (0-100)",
                "computation": "Cumulative diversity score based on: geographic regions tested, school types, grade levels, demographics. Higher score = intervention tested in MORE varied contexts over time."
            },
            "bubble_size": {
                "label": "Cumulative Students Impacted",
                "description": "Total students studied up to that point in time",
                "computation": "Cumulative sum of unique students across all studies up to each time point. Represents total evidence base."
            }
        }

        return {
            "time_series": time_series,
            "individual_interventions": individual_interventions,
            "metadata": metadata
        }

    def _compute_time_series_for_io(self, io: str, color: str) -> Dict[str, Any]:
        """Compute time series data for a single IO using 3-year buckets."""

        # Define 3-year periods from 1984 to 2025 (covers full WWC data range)
        periods = []
        for start_year in range(1984, 2026, 3):
            end_year = min(start_year + 2, 2025)
            periods.append((start_year, end_year))

        # Get all WWC papers for this IO - ONLY highest quality RCTs
        # Filter: "Meets WWC standards without reservations" + RCT design
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND p.wwc_study_rating = 'Meets WWC standards without reservations'
                  AND p.study_design =~ '(?i).*randomized.*'
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                RETURN
                    p.title as title,
                    p.year as year,
                    p.population as population,
                    f.study_size as study_size,
                    f.effect_size as effect_size,
                    f.region as region,
                    f.school_type as school_type
            """, io=io)

            all_findings = [dict(record) for record in result]

        # Group by unique studies and track cumulative metrics
        data_points = []
        cumulative_contexts = {'regions': set(), 'school_types': set(), 'populations': set()}
        cumulative_students_by_study = {}  # Track unique studies to avoid double-counting

        for start_year, end_year in periods:
            # Findings published in this period
            period_findings = [f for f in all_findings
                             if f.get('year') and start_year <= f['year'] <= end_year]

            # Update cumulative students (group by study to avoid double-counting)
            for finding in period_findings:
                title = finding.get('title')
                size = finding.get('study_size', 0)
                if title and size:
                    if title not in cumulative_students_by_study or size > cumulative_students_by_study[title]:
                        cumulative_students_by_study[title] = size

            # Update cumulative contexts
            for f in period_findings:
                if f.get('region') and f.get('region') != 'not_reported':
                    cumulative_contexts['regions'].add(f['region'])
                if f.get('school_type') and f.get('school_type') != 'not_reported':
                    cumulative_contexts['school_types'].add(f['school_type'])
                if f.get('population') and f.get('population') != 'not_reported':
                    cumulative_contexts['populations'].add(f['population'])

            # Calculate generalizability score (0-100)
            generalizability = self._calculate_generalizability_score(cumulative_contexts)

            # Cumulative students
            cumulative_students = sum(cumulative_students_by_study.values())

            # Period-specific students
            period_students_by_study = {}
            for finding in period_findings:
                title = finding.get('title')
                size = finding.get('study_size', 0)
                if title and size:
                    if title not in period_students_by_study or size > period_students_by_study[title]:
                        period_students_by_study[title] = size
            new_students_this_period = sum(period_students_by_study.values())

            # Average effect size for THIS period
            effect_sizes = [f.get('effect_size') for f in period_findings
                          if f.get('effect_size') is not None]
            avg_effect_size = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

            # Get unique studies in this period
            period_studies = set(f.get('title') for f in period_findings if f.get('title'))

            data_points.append({
                "period": f"{start_year}-{end_year}",
                "year_midpoint": (start_year + end_year) / 2,
                "generalizability_score": generalizability,
                "cumulative_students": cumulative_students,
                "new_students_this_period": new_students_this_period,
                "avg_effect_size": round(abs(avg_effect_size), 3) if avg_effect_size else 0,
                "num_studies": len(period_studies),
                "contexts": {
                    "regions": list(cumulative_contexts['regions']),
                    "school_types": list(cumulative_contexts['school_types']),
                    "populations": list(cumulative_contexts['populations'])
                }
            })

        return {
            "id": io,
            "label": io,
            "color": color,
            "data_points": data_points
        }

    def _calculate_generalizability_score(self, cumulative_contexts: Dict) -> float:
        """
        Calculate generalizability/scope expansion score (0-100).
        Based on cumulative diversity across regions, school types, populations.
        """
        # Weight different context types
        region_score = min(40, len(cumulative_contexts['regions']) * 2)  # Max 40 pts (20 regions)
        school_type_score = min(30, len(cumulative_contexts['school_types']) * 10)  # Max 30 pts (3 types)
        population_score = min(30, len(cumulative_contexts['populations']) * 5)  # Max 30 pts (6 pops)

        total = region_score + school_type_score + population_score
        return round(total, 2)

    def _get_individual_interventions_for_io(self, io: str, base_color: str) -> List[Dict[str, Any]]:
        """
        Get time series data for individual interventions within an IO.
        Used for drill-down views (Views 2-5).
        """
        import csv
        import os

        # Build mapping from study_id to intervention_name from CSV
        csv_path = os.path.join(os.path.dirname(__file__), '../../../kg-viz-frontend/WWC Analysis/Interventions_Studies_And_Findings.csv')

        study_to_intervention = {}
        intervention_names = set()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    study_id = row.get('s_StudyID', '').strip()
                    intervention_name = row.get('i_Intervention_Name', '').strip()
                    if study_id and intervention_name:
                        study_to_intervention[study_id] = intervention_name
                        intervention_names.add(intervention_name)
        except FileNotFoundError:
            print(f"Warning: CSV file not found at {csv_path}, falling back to study titles")
            # Fallback to old behavior if CSV not found
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                    WHERE (io.type = $io OR io.name = $io)
                      AND p.wwc_study_rating = 'Meets WWC standards without reservations'
                      AND p.study_design =~ '(?i).*randomized.*'
                    RETURN DISTINCT p.title as intervention_name
                    LIMIT 10
                """, io=io)
                intervention_names = {record['intervention_name'] for record in result}

        # Get all studies for this IO and map them to interventions
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND p.wwc_study_rating = 'Meets WWC standards without reservations'
                  AND p.study_design =~ '(?i).*randomized.*'
                RETURN DISTINCT p.wwc_study_id as study_id, p.year as year
            """, io=io)

            studies = [dict(record) for record in result]

        # Group studies by intervention
        intervention_studies = {}
        for study in studies:
            study_id = str(study.get('study_id', ''))
            intervention_name = study_to_intervention.get(study_id)

            if intervention_name:
                if intervention_name not in intervention_studies:
                    intervention_studies[intervention_name] = []
                intervention_studies[intervention_name].append(study)

        # Sort by number of studies and take top 10
        sorted_interventions = sorted(
            intervention_studies.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]

        # Generate unique colors for each intervention
        colors = [
            "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444",
            "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#84cc16"
        ]

        # For each intervention, compute its time series
        intervention_series = []
        for idx, (intervention_name, studies_list) in enumerate(sorted_interventions):
            years = [s['year'] for s in studies_list if s.get('year')]

            # Use unique color for each intervention
            intervention_color = colors[idx % len(colors)]

            # Compute time series for this intervention
            series = self._compute_time_series_for_intervention_by_name(intervention_name, intervention_color, io, study_to_intervention)
            series['first_year'] = min(years) if years else None
            intervention_series.append(series)

        return intervention_series

    def _compute_time_series_for_intervention_by_name(self, intervention_name: str, color: str, io: str, study_to_intervention: dict) -> Dict[str, Any]:
        """Compute time series for a specific intervention by name (from CSV mapping)."""

        # Get study IDs that belong to this intervention
        study_ids_for_intervention = [
            study_id for study_id, int_name in study_to_intervention.items()
            if int_name == intervention_name
        ]

        if not study_ids_for_intervention:
            return {
                "id": intervention_name,
                "label": intervention_name,
                "color": color,
                "data_points": []
            }

        # Define 3-year periods
        periods = []
        for start_year in range(1984, 2026, 3):
            end_year = min(start_year + 2, 2025)
            periods.append((start_year, end_year))

        # Get findings for all studies in this intervention
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC'})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND p.wwc_study_id IN $study_ids
                  AND p.wwc_study_rating = 'Meets WWC standards without reservations'
                  AND p.study_design =~ '(?i).*randomized.*'
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                RETURN
                    p.year as year,
                    p.title as study_title,
                    f.study_size as study_size,
                    f.effect_size as effect_size,
                    f.region as region,
                    f.school_type as school_type,
                    p.population as population
            """, io=io, study_ids=study_ids_for_intervention)

            findings = [dict(record) for record in result]

        # Process similar to aggregated view
        data_points = []
        cumulative_contexts = {'regions': set(), 'school_types': set(), 'populations': set()}
        cumulative_students_by_study = {}

        for start_year, end_year in periods:
            period_findings = [f for f in findings
                             if f.get('year') and start_year <= f['year'] <= end_year]

            # Update cumulative students (group by study to avoid double-counting)
            for finding in period_findings:
                title = finding.get('study_title')
                size = finding.get('study_size', 0)
                if title and size:
                    if title not in cumulative_students_by_study or size > cumulative_students_by_study[title]:
                        cumulative_students_by_study[title] = size

            # Update contexts
            for f in period_findings:
                if f.get('region') and f.get('region') != 'not_reported':
                    cumulative_contexts['regions'].add(f['region'])
                if f.get('school_type') and f.get('school_type') != 'not_reported':
                    cumulative_contexts['school_types'].add(f['school_type'])
                if f.get('population') and f.get('population') != 'not_reported':
                    cumulative_contexts['populations'].add(f['population'])

            generalizability = self._calculate_generalizability_score(cumulative_contexts)
            cumulative_students = sum(cumulative_students_by_study.values())

            # Period-specific students
            period_students_by_study = {}
            for finding in period_findings:
                title = finding.get('study_title')
                size = finding.get('study_size', 0)
                if title and size:
                    if title not in period_students_by_study or size > period_students_by_study[title]:
                        period_students_by_study[title] = size
            new_students_this_period = sum(period_students_by_study.values())

            # Effect sizes
            effect_sizes = [f.get('effect_size') for f in period_findings if f.get('effect_size') is not None]
            avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

            # Get unique studies in this period
            period_studies = set(f.get('study_title') for f in period_findings if f.get('study_title'))

            data_points.append({
                "period": f"{start_year}-{end_year}",
                "year_midpoint": (start_year + end_year) / 2,
                "generalizability_score": generalizability,
                "cumulative_students": cumulative_students,
                "new_students_this_period": new_students_this_period,
                "avg_effect_size": round(abs(avg_effect), 3) if avg_effect else 0,
                "num_studies": len(period_studies),
                "contexts": {
                    "regions": list(cumulative_contexts['regions']),
                    "school_types": list(cumulative_contexts['school_types']),
                    "populations": list(cumulative_contexts['populations'])
                }
            })

        return {
            "id": intervention_name,
            "label": intervention_name,
            "color": color,
            "data_points": data_points
        }

    def _compute_time_series_for_intervention(self, intervention_name: str, color: str, io: str) -> Dict[str, Any]:
        """Compute time series for a specific intervention (legacy method using study title)."""

        # Define 3-year periods
        periods = []
        for start_year in range(1984, 2026, 3):
            end_year = min(start_year + 2, 2025)
            periods.append((start_year, end_year))

        # Get findings for this specific intervention
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Paper {source: 'WWC', title: $intervention_name})-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
                WHERE (io.type = $io OR io.name = $io)
                  AND p.wwc_study_rating = 'Meets WWC standards without reservations'
                  AND p.study_design =~ '(?i).*randomized.*'
                MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding {source: 'WWC'})
                RETURN
                    p.year as year,
                    f.study_size as study_size,
                    f.effect_size as effect_size,
                    f.region as region,
                    f.school_type as school_type,
                    p.population as population
            """, intervention_name=intervention_name, io=io)

            findings = [dict(record) for record in result]

        # Process similar to aggregated view
        data_points = []
        cumulative_contexts = {'regions': set(), 'school_types': set(), 'populations': set()}
        cumulative_students = 0

        for start_year, end_year in periods:
            period_findings = [f for f in findings
                             if f.get('year') and start_year <= f['year'] <= end_year]

            # Update cumulative students
            period_students = sum(f.get('study_size', 0) for f in period_findings if f.get('study_size'))
            cumulative_students += period_students

            # Update contexts
            for f in period_findings:
                if f.get('region') and f.get('region') != 'not_reported':
                    cumulative_contexts['regions'].add(f['region'])
                if f.get('school_type') and f.get('school_type') != 'not_reported':
                    cumulative_contexts['school_types'].add(f['school_type'])
                if f.get('population') and f.get('population') != 'not_reported':
                    cumulative_contexts['populations'].add(f['population'])

            generalizability = self._calculate_generalizability_score(cumulative_contexts)

            # Effect sizes
            effect_sizes = [f.get('effect_size') for f in period_findings if f.get('effect_size') is not None]
            avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0

            data_points.append({
                "period": f"{start_year}-{end_year}",
                "year_midpoint": (start_year + end_year) / 2,
                "generalizability_score": generalizability,
                "cumulative_students": cumulative_students,
                "new_students_this_period": period_students,
                "avg_effect_size": round(abs(avg_effect), 3) if avg_effect else 0,
                "num_studies": len(period_findings),
                "contexts": {
                    "regions": list(cumulative_contexts['regions']),
                    "school_types": list(cumulative_contexts['school_types']),
                    "populations": list(cumulative_contexts['populations'])
                }
            })

        return {
            "id": intervention_name,
            "label": intervention_name,
            "color": color,
            "data_points": data_points
        }

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

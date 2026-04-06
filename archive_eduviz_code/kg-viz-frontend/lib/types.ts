/**
 * TypeScript types for visualization data
 */

export interface BubbleData {
  id: string;
  label: string;
  x: number; // Evidence maturity (0-100)
  y: number; // Problem burden scale OR potential impact
  size: number; // Bubble size
  color: string | null;
  priority: 'high_priority' | 'on_watch' | 'research_gap'; // Priority tag
  paper_count: number;
  breakdown: BreakdownData;
}

export interface BreakdownData {
  evidence_maturity: EvidenceMaturityBreakdown;
  problem_scale?: ProblemScaleBreakdown;
  effort_required?: EffortRequiredBreakdown;
  investment?: InvestmentBreakdown;
  potential_impact?: PotentialImpactBreakdown;
  r_and_d_required?: RAndDBreakdown;
  study_design_distribution?: Record<string, number>;
  // Level 3 specific
  external_validity?: ExternalValidityBreakdown;
  students_impacted?: StudentsImpactedBreakdown;
  effect_summary?: EffectSummaryBreakdown;
  wwc_ratings?: Record<string, number>;
}

export interface EvidenceMaturityBreakdown {
  score: number;
  max: number;
  description: string;
  components: {
    design_strength: ComponentScore;
    consistency: ComponentScore;
    external_validity: ComponentScore;
    quality: ComponentScore;
  };
}

export interface ComponentScore {
  score: number;
  max: number;
  description: string;
}

export interface ProblemScaleBreakdown {
  score: number;
  min: number;
  max: number;
  description: string;
  distribution: Record<string, number>;
}

export interface EffortRequiredBreakdown {
  score: number;
  description: string;
  components: {
    system_impact: {
      score: number;
      description: string;
    };
    decision_complexity: {
      score: number;
      description: string;
    };
  };
}

export interface InvestmentBreakdown {
  amount: number;
  formatted: string;
  description: string;
}

export interface PotentialImpactBreakdown {
  score: number;
  description: string;
  outcomes_targeted: string[];
}

export interface RAndDBreakdown {
  score: number;
  description: string;
  components: {
    evidence_maturity_gap: {
      score: number;
      description: string;
    };
    evaluation_burden: {
      score: number;
      description: string;
    };
  };
}

export interface ExternalValidityBreakdown {
  score: number;
  max: number;
  description: string;
  regions_covered?: string[];
}

export interface StudentsImpactedBreakdown {
  score: number;
  description: string;
  components: {
    total_students: {
      score: number;
      description: string;
    };
    avg_per_study: {
      score: number;
      description: string;
    };
  };
}

export interface EffectSummaryBreakdown {
  average_effect_size: number;
  num_findings: number;
  significant_rate: number;
  description: string;
}

export interface VisualizationResponse {
  bubbles: BubbleData[];
  metadata: {
    x_axis: AxisMetadata;
    y_axis: AxisMetadata;
    bubble_size: BubbleSizeMetadata;
    investments?: Record<string, number>;
  };
}

export interface AxisMetadata {
  label: string;
  description: string;
  computation: string;
  median?: number;
}

export interface BubbleSizeMetadata {
  label: string;
  description: string;
  computation: string;
}

// Level 5: Time Series Types
export interface TimeSeriesDataPoint {
  period: string;
  year_midpoint: number;
  generalizability_score: number;
  cumulative_students: number;
  new_students_this_period: number;
  avg_effect_size: number;
  num_studies: number;
  contexts: {
    regions: string[];
    school_types: string[];
    populations: string[];
  };
}

export interface TimeSeriesData {
  id: string;
  label: string;
  color: string;
  data_points: TimeSeriesDataPoint[];
  first_year?: number;
}

export interface Level5Response {
  time_series: TimeSeriesData[];
  individual_interventions: {
    [io: string]: TimeSeriesData[];
  };
  metadata: {
    x_axis: AxisMetadata;
    y_axis: AxisMetadata;
    bubble_size: BubbleSizeMetadata;
  };
}

// P5: Delivery Pillar Types
export interface P5GeographicDataPoint {
  state: string;
  student_count: number;
  study_count: number;
  interventions?: { [key: string]: number };
}

export interface P5DemographicDataPoint {
  state: string;
  category: string;
  student_count: number;
  percentage: number;
}

export interface P5InstitutionDataPoint {
  state: string;
  institution_type: string;
  count: number;
  percentage: number;
}

export interface P5GradeLevelDataPoint {
  state: string;
  grade_level: string;
  student_count: number;
  percentage: number;
}

export interface P5TimeSlice {
  year: number;
  geographic_data: P5GeographicDataPoint[];
  demographic_data: P5DemographicDataPoint[];
  institution_data: P5InstitutionDataPoint[];
  grade_level_data: P5GradeLevelDataPoint[];
  total_students: number;
  total_studies: number;
}

export interface P5Response {
  time_slices: P5TimeSlice[];
  all_years: number[];
  metadata: {
    pillar: string;
    description: string;
    icon_scale: {
      person: string;
      building: string;
    };
    filters_applied: string[];
  };
}

// P1: Effect Size Over Time Types

export interface P1Finding {
  effect_size: number;
  outcome_measure: string;
  outcome_domain: string; // Domain category (e.g., Alphabetics, Phonology)
  period: string; // Timing of measurement (e.g., immediate, 1 Year follow-up)
  sample_description: string; // Sample or subgroup details
  is_subgroup: boolean; // Whether this is a subgroup analysis
  intervention_mean: number | null; // Intervention group mean score
  comparison_mean: number | null; // Control/comparison group mean score
  comparison_clusters: number | null; // Number of schools/sites in control group (for cluster RCTs)
  is_significant: boolean;
  direction: string; // Favorable, Unfavorable, No discernable effect size direction
}

export interface P1Study {
  study_id: string;
  citation: string;
  sample_size: number;
  intervention_name?: string; // Intervention name (for use-case view)
  findings: P1Finding[];
}

export interface P1DataPoint {
  year: number;
  effect_size: number;
  new_students: number;
  cumulative_students: number;
  num_findings: number;
  num_studies: number;
  dominant_direction: string;
  studies: P1Study[];
}

export interface P1Series {
  id: string;
  label: string;
  color: string;
  use_case?: string;
  data_points: P1DataPoint[];
}

export interface P1Response {
  intervention_series: P1Series[];
  usecase_series: P1Series[];
  metadata: {
    x_axis: AxisMetadata;
    y_axis: AxisMetadata;
    bubble_size: BubbleSizeMetadata;
    bubble_color: {
      label: string;
      description: string;
      values: {
        [key: string]: string;
      };
    };
  };
}

// Gates Investment Overlap Types
export interface GatesStateData {
  state: string;
  investment_amount: number;
}

export interface WWCDistributionData {
  state: string;
  student_count: number;
  study_count: number;
}

export interface GatesInvestmentResponse {
  state_data: GatesStateData[];
  wwc_distribution: WWCDistributionData[];
  total_investment: number;
  state_allocated_investment: number;
  unallocated_investment: number;
  states_with_specific_investment: number;
  metadata: {
    title: string;
    description: string;
    total_investments: number;
    color_scale: string;
  };
}

// P1Current: Evidence Ladder Types
export interface P1CurrentPaper {
  title: string;
  url?: string;
  year?: number;
  study_design?: string;
  population?: string;
  outcomes: string[];
}

export interface P1CurrentRung {
  rung_number: number;
  rung_name: string;
  description: string;
  paper_count: number;
  papers: P1CurrentPaper[];
}

export interface P1CurrentResponse {
  rungs: P1CurrentRung[];
  total_papers: number;
  implementation_objective: string;
  metadata: {
    title: string;
    description: string;
    classifications: {
      [key: string]: string[];
    };
  };
}

export interface P1CurrentUseCaseLadder {
  use_case_id: string;
  use_case_label: string;
  rungs: P1CurrentRung[];
}

export interface P1CurrentByCaseResponse {
  use_case_ladders: P1CurrentUseCaseLadder[];
  total_papers: number;
  implementation_objective: string;
  metadata: {
    title: string;
    description: string;
    use_cases: string[];
  };
}

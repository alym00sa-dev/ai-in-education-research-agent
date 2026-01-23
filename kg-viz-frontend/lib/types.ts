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

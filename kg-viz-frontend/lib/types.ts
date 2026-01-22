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

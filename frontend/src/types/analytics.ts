export interface RiskMatrixCell {
  department: string;
  risk_band: "low" | "medium" | "high" | "critical";
  count: number;
}

export interface InvestigationTimelinePoint {
  week: string;
  total: number;
  resolved: number;
  dismissed: number;
  pending: number;
}

export interface ReviewerActivity {
  reviewer_name: string;
  total_decided: number;
  resolved: number;
  dismissed: number;
}

export interface AnalyticsData {
  risk_matrix: RiskMatrixCell[];
  investigation_timeline: InvestigationTimelinePoint[];
  reviewer_activity: ReviewerActivity[];
}

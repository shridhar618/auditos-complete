export interface KPISummary {
  compliance_score: number;
  risk_score: number;
  critical_violations: number;
  pending_investigations: number;
  open_cases: number;
  resolved_cases: number;
  total_transactions: number;
}

export interface MonthlyTrendPoint {
  month: string;
  total_transactions: number;
  flagged_transactions: number;
  violations: number;
}

export interface DepartmentRisk {
  department: string;
  avg_risk_score: number;
  transaction_count: number;
  violation_count: number;
}

export interface VendorRisk {
  vendor: string;
  avg_risk_score: number;
  transaction_count: number;
}

export interface RecentActivityItem {
  action: string;
  resource_type: string;
  resource_id: string | null;
  actor_name: string | null;
  created_at: string;
}

export interface DashboardSummary {
  kpis: KPISummary;
  monthly_trend: MonthlyTrendPoint[];
  department_risk: DepartmentRisk[];
  vendor_risk: VendorRisk[];
  recent_activity: RecentActivityItem[];
}

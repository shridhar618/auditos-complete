export type InvestigationStatus = "open" | "pending_approval" | "resolved" | "dismissed";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface PolicyViolation {
  rule_id: string;
  rule_name: string;
  description: string;
}

export interface AgentRunLog {
  agent_name: string;
  step_order: number;
  input_summary: string | null;
  output_summary: string | null;
  reasoning: string | null;
  metadata_json: Record<string, unknown> | null;
  used_llm: boolean;
  created_at: string;
}

export interface Investigation {
  id: string;
  transaction_id: string | null;
  transaction_reference: string | null;
  status: InvestigationStatus;
  risk_level: RiskLevel;
  summary: string | null;
  recommendation: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface InvestigationDetail extends Investigation {
  evidence_json: {
    transaction_snapshot?: {
      reference_code: string | null;
      amount: number | null;
      currency: string | null;
      transaction_date: string | null;
    };
    risk_score?: number;
    detection_reasoning?: string;
    policy_violations?: PolicyViolation[];
  } | null;
  resolution_notes: string | null;
  agent_logs: AgentRunLog[];
}

export interface InvestigationListResponse {
  items: Investigation[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AgentPipelineResult {
  transaction_id: string;
  risk_score: number;
  is_anomalous: boolean;
  should_investigate: boolean;
  investigation_id: string | null;
  policy_violations: PolicyViolation[];
  recommendation: string | null;
}

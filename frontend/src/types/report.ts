export type ReportType = "audit" | "risk" | "compliance" | "department" | "vendor";
export type ReportFormat = "pdf" | "excel" | "csv";

export interface AuditReport {
  id: string;
  title: string;
  report_type: ReportType;
  format: ReportFormat;
  file_size_bytes: number;
  date_from: string | null;
  date_to: string | null;
  created_at: string;
}

export interface GenerateReportPayload {
  report_type: ReportType;
  format: ReportFormat;
  date_from?: string;
  date_to?: string;
}

import { useState } from "react";
import { Download, FileBarChart, FileSpreadsheet, FileText, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/native-select";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { downloadReport, useGenerateReport, useReports } from "@/hooks/useReports";
import type { ReportFormat, ReportType } from "@/types/report";

const REPORT_TYPE_OPTIONS: { value: ReportType; label: string }[] = [
  { value: "audit", label: "Audit Investigation Report" },
  { value: "risk", label: "Risk Assessment Report" },
  { value: "compliance", label: "Compliance Report" },
  { value: "department", label: "Department Report" },
  { value: "vendor", label: "Vendor Report" },
];

const FORMAT_OPTIONS: { value: ReportFormat; label: string; icon: typeof FileText }[] = [
  { value: "pdf", label: "PDF", icon: FileText },
  { value: "excel", label: "Excel", icon: FileSpreadsheet },
  { value: "csv", label: "CSV", icon: FileBarChart },
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ReportsPage() {
  const { hasPermission } = useAuth();
  const [reportType, setReportType] = useState<ReportType>("audit");
  const [format, setFormat] = useState<ReportFormat>("pdf");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data: reports, isLoading } = useReports();
  const generateReport = useGenerateReport();

  const handleGenerate = async () => {
    await generateReport.mutateAsync({
      report_type: reportType,
      format,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground">Generate and export audit, risk, compliance, department, and vendor reports.</p>
      </div>

      {hasPermission("reports:generate") && (
        <Card>
          <CardHeader>
            <CardTitle>Generate a Report</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-2">
                <Label>Report type</Label>
                <NativeSelect value={reportType} onChange={(e) => setReportType(e.target.value as ReportType)}>
                  {REPORT_TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </NativeSelect>
              </div>
              <div className="space-y-2">
                <Label>Format</Label>
                <NativeSelect value={format} onChange={(e) => setFormat(e.target.value as ReportFormat)}>
                  {FORMAT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </NativeSelect>
              </div>
              <div className="space-y-2">
                <Label>From (optional)</Label>
                <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>To (optional)</Label>
                <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
              </div>
            </div>
            <Button onClick={handleGenerate} disabled={generateReport.isPending}>
              {generateReport.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Generate Report
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Report History</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !reports || reports.length === 0 ? (
            <EmptyState icon={FileBarChart} title="No reports generated yet" description="Use the form above to generate your first report." />
          ) : (
            <div className="divide-y divide-border">
              {reports.map((report) => (
                <div key={report.id} className="flex items-center justify-between gap-4 p-4">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{report.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {report.format.toUpperCase()} · {formatBytes(report.file_size_bytes)} ·{" "}
                      {new Date(report.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => downloadReport(report.id, report.title, report.format)}
                  >
                    <Download className="h-4 w-4" />
                    Download
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

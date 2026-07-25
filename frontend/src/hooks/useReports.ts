import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient, tokenStorage } from "@/lib/api-client";
import type { AuditReport, GenerateReportPayload } from "@/types/report";

export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: async () => {
      const { data } = await apiClient.get<AuditReport[]>("/reports");
      return data;
    },
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: GenerateReportPayload) => {
      const { data } = await apiClient.post<AuditReport>("/reports/generate", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export async function downloadReport(reportId: string, title: string, format: string) {
  const token = tokenStorage.getAccessToken();
  const response = await fetch(`/api/v1/reports/${reportId}/download`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  const ext = format === "excel" ? "xlsx" : format;
  a.href = url;
  a.download = `${title.replace(/\s+/g, "_")}.${ext}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

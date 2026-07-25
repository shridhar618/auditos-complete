import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { DashboardSummary } from "@/types/dashboard";

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardSummary>("/dashboard/summary");
      return data;
    },
    staleTime: 60_000,
  });
}

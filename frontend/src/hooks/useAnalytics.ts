import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { AnalyticsData } from "@/types/analytics";

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: async () => {
      const { data } = await apiClient.get<AnalyticsData>("/analytics");
      return data;
    },
  });
}

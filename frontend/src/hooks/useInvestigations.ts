import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type {
  AgentPipelineResult,
  AgentRunLog,
  Investigation,
  InvestigationDetail,
  InvestigationListResponse,
  InvestigationStatus,
} from "@/types/investigation";

export function useInvestigations(status: InvestigationStatus | "" , page: number, pageSize = 20) {
  return useQuery({
    queryKey: ["investigations", status, page, pageSize],
    queryFn: async () => {
      const { data } = await apiClient.get<InvestigationListResponse>("/investigations", {
        params: { status: status || undefined, page, page_size: pageSize },
      });
      return data;
    },
    placeholderData: (previous) => previous,
  });
}

export function useInvestigation(id: string | undefined) {
  return useQuery({
    queryKey: ["investigations", id],
    queryFn: async () => {
      const { data } = await apiClient.get<InvestigationDetail>(`/investigations/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useResolveInvestigation(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (resolution_notes: string | undefined) => {
      const { data } = await apiClient.post<Investigation>(`/investigations/${id}/resolve`, { resolution_notes });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDismissInvestigation(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (resolution_notes: string | undefined) => {
      const { data } = await apiClient.post<Investigation>(`/investigations/${id}/dismiss`, { resolution_notes });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useRunAgentPipeline() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (transactionId: string) => {
      const { data } = await apiClient.post<AgentPipelineResult>(`/agents/run/${transactionId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["agent-runs"] });
    },
  });
}

export function useRecentAgentRuns() {
  return useQuery({
    queryKey: ["agent-runs", "recent"],
    queryFn: async () => {
      const { data } = await apiClient.get<AgentRunLog[]>("/agents/runs/recent");
      return data;
    },
  });
}

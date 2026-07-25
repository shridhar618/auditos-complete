import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { AuditDocument } from "@/types/document";
import type { PolicySearchResponse } from "@/types/document";

export function useUploadPolicyDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post<AuditDocument>("/policies/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useSearchPolicies() {
  return useMutation({
    mutationFn: async (query: string) => {
      const { data } = await apiClient.post<PolicySearchResponse>("/policies/search", { query });
      return data;
    },
  });
}

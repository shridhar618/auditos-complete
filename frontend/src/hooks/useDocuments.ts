import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type { AuditDocument, AuditDocumentDetail, DocumentCategory } from "@/types/document";

export function useDocuments(category: DocumentCategory | "") {
  return useQuery({
    queryKey: ["documents", category],
    queryFn: async () => {
      const { data } = await apiClient.get<AuditDocument[]>("/documents", {
        params: { category: category || undefined },
      });
      return data;
    },
  });
}

export function useDocument(id: string | undefined) {
  return useQuery({
    queryKey: ["documents", "detail", id],
    queryFn: async () => {
      const { data } = await apiClient.get<AuditDocumentDetail>(`/documents/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ file, category }: { file: File; category: DocumentCategory }) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("category", category);
      const { data } = await apiClient.post<AuditDocument>("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/documents/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

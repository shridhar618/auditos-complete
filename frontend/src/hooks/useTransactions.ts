import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import type {
  CreateTransactionPayload,
  LookupOption,
  Transaction,
  TransactionFilters,
  TransactionListResponse,
} from "@/types/transaction";

function toQueryParams(filters: TransactionFilters) {
  const params: Record<string, string | number> = { page: filters.page, page_size: filters.page_size };
  if (filters.status) params.status = filters.status;
  if (filters.department_id) params.department_id = filters.department_id;
  if (filters.vendor_id) params.vendor_id = filters.vendor_id;
  if (filters.search) params.search = filters.search;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  return params;
}

export function useTransactions(filters: TransactionFilters) {
  return useQuery({
    queryKey: ["transactions", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<TransactionListResponse>("/transactions", {
        params: toQueryParams(filters),
      });
      return data;
    },
    placeholderData: (previousData) => previousData,
  });
}

export function useTransaction(id: string | undefined) {
  return useQuery({
    queryKey: ["transactions", id],
    queryFn: async () => {
      const { data } = await apiClient.get<Transaction>(`/transactions/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateTransactionPayload) => {
      const { data } = await apiClient.post<Transaction>("/transactions", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDepartments() {
  return useQuery({
    queryKey: ["lookups", "departments"],
    queryFn: async () => {
      const { data } = await apiClient.get<LookupOption[]>("/lookups/departments");
      return data;
    },
  });
}

export function useVendors() {
  return useQuery({
    queryKey: ["lookups", "vendors"],
    queryFn: async () => {
      const { data } = await apiClient.get<LookupOption[]>("/lookups/vendors");
      return data;
    },
  });
}

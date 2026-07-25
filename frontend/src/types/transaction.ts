export type TransactionStatus = "normal" | "flagged" | "under_investigation" | "violation" | "cleared";

export interface Transaction {
  id: string;
  reference_code: string;
  description: string | null;
  amount: number;
  currency: string;
  transaction_date: string;
  status: TransactionStatus;
  risk_score: number;
  is_policy_violation: boolean;
  department_name: string | null;
  vendor_name: string | null;
  created_at: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TransactionFilters {
  status?: TransactionStatus;
  department_id?: string;
  vendor_id?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
  page: number;
  page_size: number;
}

export interface CreateTransactionPayload {
  department_id?: string;
  vendor_id?: string;
  description?: string;
  amount: number;
  currency: string;
  transaction_date: string;
}

export interface LookupOption {
  id: string;
  name: string;
}

export type DocumentCategory =
  | "invoice"
  | "purchase_order"
  | "contract"
  | "bank_statement"
  | "email"
  | "policy"
  | "other";

export type DocumentStatus = "processing" | "ready" | "failed";

export interface AuditDocument {
  id: string;
  original_filename: string;
  content_type: string | null;
  file_size_bytes: number;
  category: DocumentCategory;
  status: DocumentStatus;
  extraction_method: string | null;
  processing_error: string | null;
  created_at: string;
}

export interface AuditDocumentDetail extends AuditDocument {
  extracted_text: string | null;
}

export interface PolicySearchResult {
  document_name: string;
  chunk_text: string;
  search_method: "semantic" | "keyword";
}

export interface PolicySearchResponse {
  results: PolicySearchResult[];
  search_method_used: string;
}

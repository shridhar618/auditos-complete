import { useState } from "react";
import { FileText, Trash2 } from "lucide-react";

import { DocumentPreviewDialog } from "@/components/documents/DocumentPreviewDialog";
import { DocumentStatusBadge } from "@/components/documents/DocumentStatusBadge";
import { UploadDocumentDialog } from "@/components/documents/UploadDocumentDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { NativeSelect } from "@/components/ui/native-select";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { useDeleteDocument, useDocuments } from "@/hooks/useDocuments";
import type { DocumentCategory } from "@/types/document";

const CATEGORY_OPTIONS: { value: DocumentCategory | ""; label: string }[] = [
  { value: "", label: "All types" },
  { value: "invoice", label: "Invoices" },
  { value: "purchase_order", label: "Purchase Orders" },
  { value: "contract", label: "Contracts" },
  { value: "bank_statement", label: "Bank Statements" },
  { value: "email", label: "Emails" },
  { value: "other", label: "Other" },
];

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const [category, setCategory] = useState<DocumentCategory | "">("");
  const [previewId, setPreviewId] = useState<string | null>(null);
  const { hasPermission } = useAuth();
  const { data: documents, isLoading } = useDocuments(category);
  const deleteDocument = useDeleteDocument();

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Document Center</h1>
          <p className="text-muted-foreground">Invoices, purchase orders, contracts, bank statements, and more.</p>
        </div>
        {hasPermission("documents:write") && <UploadDocumentDialog />}
      </div>

      <Card>
        <CardContent className="p-4">
          <NativeSelect className="sm:w-56" value={category} onChange={(e) => setCategory(e.target.value as DocumentCategory | "")}>
            {CATEGORY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </NativeSelect>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !documents || documents.length === 0 ? (
            <EmptyState icon={FileText} title="No documents yet" description="Upload an invoice, contract, or other file to get started." />
          ) : (
            <div className="divide-y divide-border">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between gap-4 p-4">
                  <button
                    onClick={() => setPreviewId(doc.id)}
                    className="flex min-w-0 flex-1 items-center gap-3 text-left"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{doc.original_filename}</p>
                      <p className="text-xs text-muted-foreground">
                        {doc.category.replace("_", " ")} · {formatBytes(doc.file_size_bytes)} ·{" "}
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </button>
                  <DocumentStatusBadge status={doc.status} />
                  {hasPermission("documents:write") && (
                    <Button variant="ghost" size="icon" onClick={() => deleteDocument.mutate(doc.id)}>
                      <Trash2 className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <DocumentPreviewDialog id={previewId} open={!!previewId} onOpenChange={(open) => !open && setPreviewId(null)} />
    </div>
  );
}

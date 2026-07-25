import { cn } from "@/lib/utils";
import type { DocumentStatus } from "@/types/document";

const CONFIG: Record<DocumentStatus, { label: string; className: string }> = {
  processing: { label: "Processing", className: "bg-warning/10 text-warning border-warning/20" },
  ready: { label: "Ready", className: "bg-success/10 text-success border-success/20" },
  failed: { label: "Failed", className: "bg-destructive/10 text-destructive border-destructive/20" },
};

export function DocumentStatusBadge({ status }: { status: DocumentStatus }) {
  const config = CONFIG[status];
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

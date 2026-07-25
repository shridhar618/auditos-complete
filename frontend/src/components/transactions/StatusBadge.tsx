import { cn } from "@/lib/utils";
import type { TransactionStatus } from "@/types/transaction";

const STATUS_CONFIG: Record<TransactionStatus, { label: string; className: string }> = {
  normal: { label: "Normal", className: "bg-success/10 text-success border-success/20" },
  flagged: { label: "Flagged", className: "bg-warning/10 text-warning border-warning/20" },
  under_investigation: { label: "Under Investigation", className: "bg-primary/10 text-primary border-primary/20" },
  violation: { label: "Violation", className: "bg-destructive/10 text-destructive border-destructive/20" },
  cleared: { label: "Cleared", className: "bg-muted text-muted-foreground border-border" },
};

export function StatusBadge({ status }: { status: TransactionStatus }) {
  const config = STATUS_CONFIG[status];
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

import { cn } from "@/lib/utils";
import type { InvestigationStatus } from "@/types/investigation";

const CONFIG: Record<InvestigationStatus, { label: string; className: string }> = {
  open: { label: "Open", className: "bg-primary/10 text-primary border-primary/20" },
  pending_approval: { label: "Pending Approval", className: "bg-warning/10 text-warning border-warning/20" },
  resolved: { label: "Resolved", className: "bg-success/10 text-success border-success/20" },
  dismissed: { label: "Dismissed", className: "bg-muted text-muted-foreground border-border" },
};

export function InvestigationStatusBadge({ status }: { status: InvestigationStatus }) {
  const config = CONFIG[status];
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

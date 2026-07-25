import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/types/investigation";

const CONFIG: Record<RiskLevel, { label: string; className: string }> = {
  low: { label: "Low", className: "bg-success/10 text-success border-success/20" },
  medium: { label: "Medium", className: "bg-warning/10 text-warning border-warning/20" },
  high: { label: "High", className: "bg-destructive/10 text-destructive border-destructive/20" },
  critical: { label: "Critical", className: "bg-destructive text-destructive-foreground border-destructive" },
};

export function RiskLevelBadge({ level }: { level: RiskLevel }) {
  const config = CONFIG[level];
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

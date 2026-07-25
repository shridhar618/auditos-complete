import { CheckCircle2, Circle, Clock, FileSearch, Lightbulb, ScanSearch, ShieldQuestion, Sparkles, UserCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import type { AgentRunLog, InvestigationStatus } from "@/types/investigation";

const AGENT_META: Record<string, { label: string; icon: LucideIcon }> = {
  detection: { label: "Detection Agent", icon: ScanSearch },
  policy: { label: "Policy Agent", icon: ShieldQuestion },
  investigation: { label: "Investigation Agent", icon: FileSearch },
  evidence: { label: "Evidence Agent", icon: FileSearch },
  recommendation: { label: "Recommendation Agent", icon: Lightbulb },
};

function HumanApprovalStep({ status }: { status: InvestigationStatus }) {
  const isDone = status === "resolved" || status === "dismissed";
  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2",
            isDone ? "border-success bg-success/10 text-success" : "border-warning bg-warning/10 text-warning"
          )}
        >
          {isDone ? <CheckCircle2 className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
        </div>
      </div>
      <div className="flex-1 pb-2">
        <p className="text-sm font-semibold">Human Approval</p>
        <p className="text-sm text-muted-foreground">
          {status === "resolved" && "A reviewer confirmed this finding and resolved the case."}
          {status === "dismissed" && "A reviewer dismissed this as a false positive; the transaction was cleared."}
          {status === "pending_approval" && "Waiting for a compliance officer or auditor to review the AI's recommendation."}
          {status === "open" && "Case is open and awaiting review."}
        </p>
      </div>
    </div>
  );
}

export function AgentTimeline({ logs, investigationStatus }: { logs: AgentRunLog[]; investigationStatus: InvestigationStatus }) {
  if (logs.length === 0) {
    return <p className="text-sm text-muted-foreground">No agent activity recorded for this case yet.</p>;
  }

  return (
    <div className="space-y-0">
      {logs.map((log, i) => {
        const meta = AGENT_META[log.agent_name] ?? { label: log.agent_name, icon: Circle };
        const Icon = meta.icon;
        return (
          <div key={i} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 border-primary bg-primary/10 text-primary">
                <Icon className="h-4 w-4" />
              </div>
              {i < logs.length - 1 && <div className="w-px flex-1 bg-border" />}
            </div>
            <div className="flex-1 pb-6">
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold">{meta.label}</p>
                {log.used_llm && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                    <Sparkles className="h-3 w-3" /> LLM-assisted
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{log.reasoning}</p>
              {log.output_summary && (
                <p className="mt-1 text-xs text-muted-foreground/80">
                  <span className="font-medium">Output: </span>
                  {log.output_summary}
                </p>
              )}
              <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground/60">
                <Clock className="h-3 w-3" />
                {new Date(log.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        );
      })}
      <div className="flex gap-4">
        <div className="flex flex-col items-center">
          <div className="w-px flex-1 bg-border" style={{ minHeight: 8 }} />
        </div>
        <div className="flex-1" />
      </div>
      <HumanApprovalStep status={investigationStatus} />
    </div>
  );
}

import { Bot, FileSearch, Lightbulb, ScanSearch, ShieldQuestion, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecentAgentRuns } from "@/hooks/useInvestigations";

const AGENT_META: Record<string, { label: string; icon: LucideIcon }> = {
  detection: { label: "Detection Agent", icon: ScanSearch },
  policy: { label: "Policy Agent", icon: ShieldQuestion },
  investigation: { label: "Investigation Agent", icon: FileSearch },
  evidence: { label: "Evidence Agent", icon: FileSearch },
  recommendation: { label: "Recommendation Agent", icon: Lightbulb },
};

const AGENT_DESCRIPTIONS = [
  { name: "Supervisor Agent", detail: "Coordinates the pipeline below via a LangGraph state machine." },
  { name: "Detection Agent", detail: "Scores transactions using statistical anomaly detection against peer history." },
  { name: "Policy Agent", detail: "Checks transactions against active threshold-based compliance rules." },
  { name: "Investigation Agent", detail: "Opens a human-reviewable case when a transaction is flagged." },
  { name: "Evidence Agent", detail: "Assembles the transaction snapshot and matched policy violations." },
  { name: "Recommendation Agent", detail: "Suggests a corrective action — advisory only, never auto-approves." },
];

export default function AiAgentsPage() {
  const { data: logs, isLoading } = useRecentAgentRuns();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">AI Agents</h1>
        <p className="text-muted-foreground">
          Every agent's decisions are logged and auditable. AI investigates — humans approve.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {AGENT_DESCRIPTIONS.map((agent) => (
          <Card key={agent.name}>
            <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
              <Bot className="h-4 w-4 text-primary" />
              <CardTitle className="text-sm">{agent.name}</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">{agent.detail}</CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Agent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !logs || logs.length === 0 ? (
            <EmptyState
              icon={Bot}
              title="No agent runs yet"
              description="Trigger the pipeline from any transaction's detail page to see activity here."
            />
          ) : (
            <ul className="space-y-3">
              {logs.map((log, i) => {
                const meta = AGENT_META[log.agent_name] ?? { label: log.agent_name, icon: Bot };
                const Icon = meta.icon;
                return (
                  <li key={i} className="flex items-start gap-3 border-b border-border pb-3 last:border-0 last:pb-0">
                    <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium">{meta.label}</p>
                        {log.used_llm && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                            <Sparkles className="h-3 w-3" /> LLM-assisted
                          </span>
                        )}
                        <span className="text-xs text-muted-foreground">{new Date(log.created_at).toLocaleString()}</span>
                      </div>
                      <p className="truncate text-sm text-muted-foreground">{log.output_summary}</p>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

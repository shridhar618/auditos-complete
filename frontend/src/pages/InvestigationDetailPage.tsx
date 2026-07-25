import { ArrowLeft, CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AgentTimeline } from "@/components/investigations/AgentTimeline";
import { InvestigationStatusBadge } from "@/components/investigations/InvestigationStatusBadge";
import { RiskLevelBadge } from "@/components/investigations/RiskLevelBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/context/AuthContext";
import { useDismissInvestigation, useInvestigation, useResolveInvestigation } from "@/hooks/useInvestigations";

export default function InvestigationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { hasPermission } = useAuth();
  const [notes, setNotes] = useState("");

  const { data: investigation, isLoading } = useInvestigation(id);
  const resolveMutation = useResolveInvestigation(id ?? "");
  const dismissMutation = useDismissInvestigation(id ?? "");

  const canApprove = hasPermission("investigations:approve");
  const isPending = investigation?.status === "open" || investigation?.status === "pending_approval";

  const handleResolve = async () => {
    await resolveMutation.mutateAsync(notes || undefined);
  };

  const handleDismiss = async () => {
    await dismissMutation.mutateAsync(notes || undefined);
  };

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/investigations">
          <ArrowLeft className="h-4 w-4" />
          Back to investigations
        </Link>
      </Button>

      {isLoading || !investigation ? (
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                Case · {investigation.transaction_reference ?? "Unlinked transaction"}
              </h1>
              <p className="text-muted-foreground">{investigation.summary}</p>
            </div>
            <div className="flex items-center gap-2">
              <RiskLevelBadge level={investigation.risk_level} />
              <InvestigationStatusBadge status={investigation.status} />
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="space-y-6 lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>AI Agent Pipeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <AgentTimeline logs={investigation.agent_logs} investigationStatus={investigation.status} />
                </CardContent>
              </Card>

              {investigation.evidence_json?.policy_violations && investigation.evidence_json.policy_violations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Policy Violations</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {investigation.evidence_json.policy_violations.map((v) => (
                      <div key={v.rule_id} className="rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm">
                        <p className="font-medium text-destructive">{v.rule_name}</p>
                        <p className="text-muted-foreground">{v.description}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>AI Recommendation</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  {investigation.recommendation || "No recommendation generated."}
                </CardContent>
              </Card>

              {canApprove && isPending && (
                <Card>
                  <CardHeader>
                    <CardTitle>Human Decision</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Textarea
                      placeholder="Optional notes about your decision…"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button
                        className="flex-1"
                        onClick={handleResolve}
                        disabled={resolveMutation.isPending || dismissMutation.isPending}
                      >
                        {resolveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                        Resolve
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={handleDismiss}
                        disabled={resolveMutation.isPending || dismissMutation.isPending}
                      >
                        {dismissMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <XCircle className="h-4 w-4" />}
                        Dismiss
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Resolve confirms this finding. Dismiss marks it a false positive and clears the transaction.
                    </p>
                  </CardContent>
                </Card>
              )}

              {investigation.resolution_notes && (
                <Card>
                  <CardHeader>
                    <CardTitle>Resolution Notes</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-muted-foreground">{investigation.resolution_notes}</CardContent>
                </Card>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

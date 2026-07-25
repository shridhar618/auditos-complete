import { ArrowLeft, Bot, Building2, Calendar, Loader2, ShieldQuestion, Truck } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { RiskIndicator } from "@/components/transactions/RiskIndicator";
import { StatusBadge } from "@/components/transactions/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { useRunAgentPipeline } from "@/hooks/useInvestigations";
import { useTransaction } from "@/hooks/useTransactions";

export default function TransactionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermission } = useAuth();
  const { data: txn, isLoading, isError } = useTransaction(id);
  const runPipeline = useRunAgentPipeline();

  const handleRunPipeline = async () => {
    if (!id) return;
    const result = await runPipeline.mutateAsync(id);
    if (result.investigation_id) {
      navigate(`/investigations/${result.investigation_id}`);
    }
  };

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link to="/transactions">
          <ArrowLeft className="h-4 w-4" />
          Back to transactions
        </Link>
      </Button>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : isError || !txn ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">Transaction not found.</CardContent>
        </Card>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{txn.reference_code}</h1>
              <p className="text-muted-foreground">{txn.description || "No description provided"}</p>
            </div>
            <StatusBadge status={txn.status} />
          </div>

          {hasPermission("investigations:write") && txn.status !== "cleared" && (
            <div className="flex justify-end">
              <Button onClick={handleRunPipeline} disabled={runPipeline.isPending}>
                {runPipeline.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
                Run AI Investigation
              </Button>
            </div>
          )}

          {runPipeline.isSuccess && !runPipeline.data.investigation_id && (
            <Card>
              <CardContent className="py-4 text-sm text-muted-foreground">
                The Detection and Policy Agents ran but found nothing anomalous — no case was opened.
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Amount</CardTitle>
              </CardHeader>
              <CardContent className="text-2xl font-bold">
                {txn.currency} {txn.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Risk Score</CardTitle>
              </CardHeader>
              <CardContent>
                <RiskIndicator score={txn.risk_score} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <CardTitle className="text-sm font-medium text-muted-foreground">Date</CardTitle>
              </CardHeader>
              <CardContent className="text-lg font-semibold">{txn.transaction_date}</CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
                <ShieldQuestion className="h-4 w-4 text-muted-foreground" />
                <CardTitle className="text-sm font-medium text-muted-foreground">Policy Violation</CardTitle>
              </CardHeader>
              <CardContent className="text-lg font-semibold">{txn.is_policy_violation ? "Yes" : "No"}</CardContent>
            </Card>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardHeader className="flex flex-row items-center gap-2 space-y-0">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <CardTitle className="text-base">Department</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">{txn.department_name ?? "Unassigned"}</CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-2 space-y-0">
                <Truck className="h-4 w-4 text-muted-foreground" />
                <CardTitle className="text-base">Vendor</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">{txn.vendor_name ?? "Unassigned"}</CardContent>
            </Card>
          </div>

          {txn.status === "normal" && !runPipeline.isSuccess && (
            <Card>
              <CardContent className="py-6 text-center text-sm text-muted-foreground">
                This transaction hasn't been scored by the Detection Agent yet. Click "Run AI Investigation"
                above to check it against peer statistics and active policy rules.
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

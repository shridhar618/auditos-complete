import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, FolderOpen, ShieldAlert, ShieldCheck } from "lucide-react";

import { DepartmentRiskChart } from "@/components/dashboard/DepartmentRiskChart";
import { KpiCard, KpiCardSkeleton } from "@/components/dashboard/KpiCard";
import { MonthlyTrendChart } from "@/components/dashboard/MonthlyTrendChart";
import { RecentActivityFeed } from "@/components/dashboard/RecentActivityFeed";
import { VendorRiskChart } from "@/components/dashboard/VendorRiskChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { useDashboardSummary } from "@/hooks/useDashboardSummary";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, isError } = useDashboardSummary();

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight">Welcome back, {user?.full_name.split(" ")[0]}</h1>
        <p className="text-muted-foreground">Here's what's happening across {user?.organization_name} today.</p>
      </motion.div>

      {isError && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Couldn't load dashboard data. Try refreshing the page.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading || !data ? (
          Array.from({ length: 4 }).map((_, i) => <KpiCardSkeleton key={i} />)
        ) : (
          <>
            <KpiCard
              label="Compliance Score"
              value={`${data.kpis.compliance_score}%`}
              icon={ShieldCheck}
              tone="success"
              hint={`Across ${data.kpis.total_transactions.toLocaleString()} transactions`}
            />
            <KpiCard
              label="Risk Score"
              value={`${data.kpis.risk_score}`}
              icon={ShieldAlert}
              tone={data.kpis.risk_score >= 50 ? "destructive" : "warning"}
              hint="Average across all transactions"
              delay={0.05}
            />
            <KpiCard
              label="Critical Violations"
              value={data.kpis.critical_violations.toLocaleString()}
              icon={AlertTriangle}
              tone="destructive"
              hint={`${data.kpis.pending_investigations} pending investigation${data.kpis.pending_investigations === 1 ? "" : "s"}`}
              delay={0.1}
            />
            <KpiCard
              label="Resolved Cases"
              value={data.kpis.resolved_cases.toLocaleString()}
              icon={CheckCircle2}
              tone="primary"
              hint={`${data.kpis.open_cases} still open`}
              delay={0.15}
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <MonthlyTrendChart data={data?.monthly_trend ?? []} isLoading={isLoading} />
        <RecentActivityFeed items={data?.recent_activity ?? []} isLoading={isLoading} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <DepartmentRiskChart data={data?.department_risk ?? []} isLoading={isLoading} />
        <VendorRiskChart data={data?.vendor_risk ?? []} isLoading={isLoading} />
      </div>

      {!isLoading && data && data.kpis.total_transactions === 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FolderOpen className="h-4 w-4 text-muted-foreground" />
              No transactions yet
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Your dashboard is fully wired up but has nothing to show yet. Once the Transaction
            Management module is live, real transactions will populate these charts automatically.
            For now, your backend includes <code className="rounded bg-muted px-1 py-0.5">app/seed_demo_data.py</code>{" "}
            to generate sample data for demos.
          </CardContent>
        </Card>
      )}
    </div>
  );
}

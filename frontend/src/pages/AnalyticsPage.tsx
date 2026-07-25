import { InvestigationTimelineChart } from "@/components/analytics/InvestigationTimelineChart";
import { ReviewerActivityTable } from "@/components/analytics/ReviewerActivityTable";
import { RiskMatrixHeatmap } from "@/components/analytics/RiskMatrixHeatmap";
import { useAnalytics } from "@/hooks/useAnalytics";

export default function AnalyticsPage() {
  const { data, isLoading } = useAnalytics();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Deeper cross-cutting views. For high-level KPIs and trends, see the Dashboard.
        </p>
      </div>

      <RiskMatrixHeatmap data={data?.risk_matrix ?? []} isLoading={isLoading} />

      <div className="grid gap-6 lg:grid-cols-2">
        <InvestigationTimelineChart data={data?.investigation_timeline ?? []} isLoading={isLoading} />
        <ReviewerActivityTable data={data?.reviewer_activity ?? []} isLoading={isLoading} />
      </div>
    </div>
  );
}

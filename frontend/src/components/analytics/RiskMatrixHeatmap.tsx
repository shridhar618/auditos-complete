import { Grid3x3 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { RiskMatrixCell } from "@/types/analytics";

const BANDS: RiskMatrixCell["risk_band"][] = ["low", "medium", "high", "critical"];
const BAND_LABELS: Record<RiskMatrixCell["risk_band"], string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

function intensityClass(count: number, max: number, band: RiskMatrixCell["risk_band"]) {
  if (count === 0) return "bg-muted/40 text-muted-foreground";
  const ratio = max > 0 ? count / max : 0;
  const palette: Record<RiskMatrixCell["risk_band"], string[]> = {
    low: ["bg-success/20", "bg-success/40", "bg-success/70"],
    medium: ["bg-warning/20", "bg-warning/40", "bg-warning/70"],
    high: ["bg-destructive/20", "bg-destructive/40", "bg-destructive/70"],
    critical: ["bg-destructive/40", "bg-destructive/70", "bg-destructive"],
  };
  const tier = ratio > 0.66 ? 2 : ratio > 0.33 ? 1 : 0;
  return `${palette[band][tier]} ${tier === 2 && band === "critical" ? "text-destructive-foreground" : ""}`;
}

export function RiskMatrixHeatmap({ data, isLoading }: { data: RiskMatrixCell[]; isLoading: boolean }) {
  const departments = Array.from(new Set(data.map((d) => d.department))).sort();
  const maxCount = Math.max(1, ...data.map((d) => d.count));

  const getCount = (department: string, band: string) => data.find((d) => d.department === department && d.risk_band === band)?.count ?? 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Matrix</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : departments.length === 0 ? (
          <EmptyState icon={Grid3x3} title="No data yet" description="The risk matrix fills in once transactions are scored by the Detection Agent." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th className="p-2 text-left text-xs font-medium text-muted-foreground">Department</th>
                  {BANDS.map((band) => (
                    <th key={band} className="p-2 text-center text-xs font-medium text-muted-foreground">
                      {BAND_LABELS[band]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {departments.map((department) => (
                  <tr key={department}>
                    <td className="p-2 text-sm font-medium">{department}</td>
                    {BANDS.map((band) => {
                      const count = getCount(department, band);
                      return (
                        <td key={band} className="p-1">
                          <div
                            className={`flex h-12 items-center justify-center rounded-md text-sm font-semibold transition-colors ${intensityClass(count, maxCount, band)}`}
                          >
                            {count}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

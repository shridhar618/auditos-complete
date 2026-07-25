import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Truck } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { VendorRisk } from "@/types/dashboard";

function riskColor(score: number) {
  if (score >= 65) return "hsl(var(--destructive))";
  if (score >= 40) return "hsl(var(--warning))";
  return "hsl(var(--accent))";
}

export function VendorRiskChart({ data, isLoading }: { data: VendorRisk[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Vendor Risk</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : data.length === 0 ? (
          <EmptyState icon={Truck} title="No vendor data yet" description="Vendor risk appears once transactions are linked to vendors." />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data} margin={{ left: -20, right: 12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="vendor" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                cursor={{ fill: "hsl(var(--muted))" }}
                contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              />
              <Bar dataKey="avg_risk_score" name="Avg. risk score" radius={[4, 4, 0, 0]}>
                {data.map((entry) => (
                  <Cell key={entry.vendor} fill={riskColor(entry.avg_risk_score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Building2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { DepartmentRisk } from "@/types/dashboard";

function riskColor(score: number) {
  if (score >= 65) return "hsl(var(--destructive))";
  if (score >= 40) return "hsl(var(--warning))";
  return "hsl(var(--success))";
}

export function DepartmentRiskChart({ data, isLoading }: { data: DepartmentRisk[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Department Risk</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : data.length === 0 ? (
          <EmptyState icon={Building2} title="No department data yet" description="Risk by department appears once transactions are tagged to departments." />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis type="category" dataKey="department" width={110} tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                cursor={{ fill: "hsl(var(--muted))" }}
                contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              />
              <Bar dataKey="avg_risk_score" name="Avg. risk score" radius={[0, 4, 4, 0]} barSize={16}>
                {data.map((entry) => (
                  <Cell key={entry.department} fill={riskColor(entry.avg_risk_score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

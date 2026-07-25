import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Clock3 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { InvestigationTimelinePoint } from "@/types/analytics";

export function InvestigationTimelineChart({ data, isLoading }: { data: InvestigationTimelinePoint[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Investigation Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : data.length === 0 ? (
          <EmptyState icon={Clock3} title="No investigations yet" description="Cases opened by the AI Agent pipeline will appear here by week." />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data} margin={{ left: -20, right: 12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" allowDecimals={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="resolved" stackId="a" name="Resolved" fill="hsl(var(--success))" radius={[0, 0, 0, 0]} />
              <Bar dataKey="dismissed" stackId="a" name="Dismissed" fill="hsl(var(--muted-foreground))" radius={[0, 0, 0, 0]} />
              <Bar dataKey="pending" stackId="a" name="Pending" fill="hsl(var(--warning))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

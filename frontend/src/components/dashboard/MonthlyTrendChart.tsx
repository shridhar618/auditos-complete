import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { MonthlyTrendPoint } from "@/types/dashboard";
import { TrendingUp } from "lucide-react";

export function MonthlyTrendChart({ data, isLoading }: { data: MonthlyTrendPoint[]; isLoading: boolean }) {
  return (
    <Card className="col-span-full lg:col-span-2">
      <CardHeader>
        <CardTitle>Monthly Audit Trend</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : data.length === 0 ? (
          <EmptyState icon={TrendingUp} title="No transaction history yet" description="Trends will appear once transactions start flowing in." />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={data} margin={{ left: -20, right: 12, top: 8 }}>
              <defs>
                <linearGradient id="fillTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="fillViolations" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Area type="monotone" dataKey="total_transactions" name="Total transactions" stroke="hsl(var(--primary))" fill="url(#fillTotal)" strokeWidth={2} />
              <Area type="monotone" dataKey="violations" name="Violations" stroke="hsl(var(--destructive))" fill="url(#fillViolations)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

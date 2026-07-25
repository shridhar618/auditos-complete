import { UserCheck } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import type { ReviewerActivity } from "@/types/analytics";

export function ReviewerActivityTable({ data, isLoading }: { data: ReviewerActivity[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Reviewer Activity</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {isLoading ? (
          <div className="space-y-2 p-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : data.length === 0 ? (
          <EmptyState icon={UserCheck} title="No decisions recorded yet" description="Once auditors resolve or dismiss cases, activity shows up here." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3 font-medium">Reviewer</th>
                <th className="px-4 py-3 text-right font-medium">Resolved</th>
                <th className="px-4 py-3 text-right font-medium">Dismissed</th>
                <th className="px-4 py-3 text-right font-medium">Total</th>
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.reviewer_name} className="border-b border-border last:border-0">
                  <td className="px-4 py-3 font-medium">{r.reviewer_name}</td>
                  <td className="px-4 py-3 text-right text-success">{r.resolved}</td>
                  <td className="px-4 py-3 text-right text-muted-foreground">{r.dismissed}</td>
                  <td className="px-4 py-3 text-right font-semibold">{r.total_decided}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
}

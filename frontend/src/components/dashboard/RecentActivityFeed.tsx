import { Activity, FileWarning, LogIn, ShieldQuestion, ShieldCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { actionLabel, formatRelativeTime } from "@/lib/format";
import type { RecentActivityItem } from "@/types/dashboard";

const ACTION_ICONS: Record<string, LucideIcon> = {
  "user.login": LogIn,
  "transaction.flagged": FileWarning,
  "investigation.opened": ShieldQuestion,
  "investigation.resolved": ShieldCheck,
};

export function RecentActivityFeed({ items, isLoading }: { items: RecentActivityItem[]; isLoading: boolean }) {
  return (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <EmptyState icon={Activity} title="No activity yet" description="Actions across your organization will show up here in real time." />
        ) : (
          <ul className="space-y-4">
            {items.map((item, i) => {
              const Icon = ACTION_ICONS[item.action] ?? Activity;
              return (
                <li key={i} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm">
                      <span className="font-medium">{item.actor_name ?? "System"}</span>{" "}
                      <span className="text-muted-foreground">{actionLabel(item.action)}</span>
                    </p>
                    <p className="text-xs text-muted-foreground">{formatRelativeTime(item.created_at)}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

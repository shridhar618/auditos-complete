import { useState } from "react";
import { ChevronLeft, ChevronRight, ShieldQuestion } from "lucide-react";
import { Link } from "react-router-dom";

import { InvestigationStatusBadge } from "@/components/investigations/InvestigationStatusBadge";
import { RiskLevelBadge } from "@/components/investigations/RiskLevelBadge";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { NativeSelect } from "@/components/ui/native-select";
import { Skeleton } from "@/components/ui/skeleton";
import { useInvestigations } from "@/hooks/useInvestigations";
import type { InvestigationStatus } from "@/types/investigation";

const STATUS_OPTIONS: { value: InvestigationStatus | ""; label: string }[] = [
  { value: "", label: "All statuses" },
  { value: "open", label: "Open" },
  { value: "pending_approval", label: "Pending Approval" },
  { value: "resolved", label: "Resolved" },
  { value: "dismissed", label: "Dismissed" },
];

export default function InvestigationsPage() {
  const [status, setStatus] = useState<InvestigationStatus | "">("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useInvestigations(status, page);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Audit Investigations</h1>
        <p className="text-muted-foreground">
          Cases opened by the AI agent pipeline. Every case waits for a human decision — resolve or dismiss.
        </p>
      </div>

      <Card>
        <CardContent className="flex items-center gap-3 p-4">
          <NativeSelect
            className="sm:w-56"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as InvestigationStatus | "");
              setPage(1);
            }}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </NativeSelect>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !data || data.items.length === 0 ? (
            <EmptyState
              icon={ShieldQuestion}
              title="No investigations found"
              description="Run the AI Agent pipeline from a transaction's detail page to open a case here."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                    <th className="px-4 py-3 font-medium">Transaction</th>
                    <th className="px-4 py-3 font-medium">Summary</th>
                    <th className="px-4 py-3 font-medium">Risk Level</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Opened</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((inv) => (
                    <tr key={inv.id} className="border-b border-border last:border-0 hover:bg-accent/50">
                      <td className="px-4 py-3">
                        <Link to={`/investigations/${inv.id}`} className="font-medium text-primary hover:underline">
                          {inv.transaction_reference ?? "—"}
                        </Link>
                      </td>
                      <td className="max-w-xs truncate px-4 py-3 text-muted-foreground">{inv.summary}</td>
                      <td className="px-4 py-3">
                        <RiskLevelBadge level={inv.risk_level} />
                      </td>
                      <td className="px-4 py-3">
                        <InvestigationStatusBadge status={inv.status} />
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{new Date(inv.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between border-t border-border px-4 py-3 text-sm">
              <p className="text-muted-foreground">
                Page {data.page} of {data.total_pages} · {data.total.toLocaleString()} cases
              </p>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="flex h-8 w-8 items-center justify-center rounded-md border border-border disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  disabled={page >= data.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                  className="flex h-8 w-8 items-center justify-center rounded-md border border-border disabled:opacity-40"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

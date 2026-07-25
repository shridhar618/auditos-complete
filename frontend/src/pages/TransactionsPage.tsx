import { useState } from "react";
import { ChevronLeft, ChevronRight, Inbox, Search } from "lucide-react";
import { Link } from "react-router-dom";

import { CreateTransactionDialog } from "@/components/transactions/CreateTransactionDialog";
import { RiskIndicator } from "@/components/transactions/RiskIndicator";
import { StatusBadge } from "@/components/transactions/StatusBadge";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { NativeSelect } from "@/components/ui/native-select";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { useDepartments, useTransactions, useVendors } from "@/hooks/useTransactions";
import type { TransactionFilters, TransactionStatus } from "@/types/transaction";

const STATUS_OPTIONS: { value: TransactionStatus | ""; label: string }[] = [
  { value: "", label: "All statuses" },
  { value: "normal", label: "Normal" },
  { value: "flagged", label: "Flagged" },
  { value: "under_investigation", label: "Under Investigation" },
  { value: "violation", label: "Violation" },
  { value: "cleared", label: "Cleared" },
];

export default function TransactionsPage() {
  const [filters, setFilters] = useState<TransactionFilters>({ page: 1, page_size: 20 });
  const [searchInput, setSearchInput] = useState("");
  const { hasPermission } = useAuth();

  const { data, isLoading, isFetching } = useTransactions(filters);
  const { data: departments } = useDepartments();
  const { data: vendors } = useVendors();

  const updateFilter = (patch: Partial<TransactionFilters>) => setFilters((prev) => ({ ...prev, ...patch, page: 1 }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Transactions</h1>
          <p className="text-muted-foreground">Continuous monitoring across every transaction in your organization.</p>
        </div>
        {hasPermission("transactions:write") && <CreateTransactionDialog />}
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by reference code or description…"
              className="pl-9"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && updateFilter({ search: searchInput || undefined })}
            />
          </div>
          <NativeSelect
            className="sm:w-48"
            value={filters.status ?? ""}
            onChange={(e) => updateFilter({ status: (e.target.value || undefined) as TransactionStatus | undefined })}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </NativeSelect>
          <NativeSelect
            className="sm:w-48"
            value={filters.department_id ?? ""}
            onChange={(e) => updateFilter({ department_id: e.target.value || undefined })}
          >
            <option value="">All departments</option>
            {departments?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </NativeSelect>
          <NativeSelect
            className="sm:w-48"
            value={filters.vendor_id ?? ""}
            onChange={(e) => updateFilter({ vendor_id: e.target.value || undefined })}
          >
            <option value="">All vendors</option>
            {vendors?.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </NativeSelect>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !data || data.items.length === 0 ? (
            <EmptyState
              icon={Inbox}
              title="No transactions found"
              description="Try adjusting your filters, or create a new transaction to get started."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                    <th className="px-4 py-3 font-medium">Reference</th>
                    <th className="px-4 py-3 font-medium">Date</th>
                    <th className="px-4 py-3 font-medium">Department</th>
                    <th className="px-4 py-3 font-medium">Vendor</th>
                    <th className="px-4 py-3 text-right font-medium">Amount</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Risk</th>
                  </tr>
                </thead>
                <tbody className={isFetching ? "opacity-60 transition-opacity" : "transition-opacity"}>
                  {data.items.map((txn) => (
                    <tr key={txn.id} className="border-b border-border last:border-0 hover:bg-accent/50">
                      <td className="px-4 py-3">
                        <Link to={`/transactions/${txn.id}`} className="font-medium text-primary hover:underline">
                          {txn.reference_code}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{txn.transaction_date}</td>
                      <td className="px-4 py-3">{txn.department_name ?? "—"}</td>
                      <td className="px-4 py-3">{txn.vendor_name ?? "—"}</td>
                      <td className="px-4 py-3 text-right tabular-nums">
                        {txn.currency} {txn.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={txn.status} />
                      </td>
                      <td className="px-4 py-3">
                        <RiskIndicator score={txn.risk_score} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between border-t border-border px-4 py-3 text-sm">
              <p className="text-muted-foreground">
                Page {data.page} of {data.total_pages} · {data.total.toLocaleString()} transactions
              </p>
              <div className="flex gap-2">
                <button
                  disabled={filters.page <= 1}
                  onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}
                  className="flex h-8 w-8 items-center justify-center rounded-md border border-border disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  disabled={filters.page >= data.total_pages}
                  onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}
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

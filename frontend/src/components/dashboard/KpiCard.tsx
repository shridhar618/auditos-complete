import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  tone?: "primary" | "success" | "warning" | "destructive" | "accent";
  hint?: string;
  delay?: number;
}

const TONE_CLASSES: Record<NonNullable<KpiCardProps["tone"]>, string> = {
  primary: "text-primary",
  success: "text-success",
  warning: "text-warning",
  destructive: "text-destructive",
  accent: "text-accent",
};

export function KpiCard({ label, value, icon: Icon, tone = "primary", hint, delay = 0 }: KpiCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
          <Icon className={cn("h-4 w-4", TONE_CLASSES[tone])} />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function KpiCardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-2">
        <Skeleton className="h-4 w-24" />
      </CardHeader>
      <CardContent className="space-y-2">
        <Skeleton className="h-7 w-16" />
        <Skeleton className="h-3 w-28" />
      </CardContent>
    </Card>
  );
}

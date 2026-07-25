export function RiskIndicator({ score }: { score: number }) {
  const color = score >= 65 ? "bg-destructive" : score >= 40 ? "bg-warning" : "bg-success";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="w-7 text-xs tabular-nums text-muted-foreground">{score}</span>
    </div>
  );
}

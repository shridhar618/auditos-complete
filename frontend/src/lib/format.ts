export function formatRelativeTime(isoDate: string): string {
  const date = new Date(isoDate);
  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.round(diffMs / 60_000);

  if (diffMinutes < 1) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.round(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

export function actionLabel(action: string): string {
  const map: Record<string, string> = {
    "user.login": "signed in",
    "transaction.flagged": "flagged a transaction",
    "investigation.opened": "opened an investigation",
    "investigation.resolved": "resolved an investigation",
    "policy.updated": "updated a policy",
  };
  return map[action] ?? action.replace(/[._]/g, " ");
}

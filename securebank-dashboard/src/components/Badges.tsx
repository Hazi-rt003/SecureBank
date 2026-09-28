const RISK_STYLES: Record<string, string> = {
  LOW: 'bg-risk-low-soft text-risk-low',
  MEDIUM: 'bg-risk-medium-soft text-risk-medium',
  HIGH: 'bg-risk-high-soft text-risk-high',
}

export function RiskBadge({ level }: { level: string }) {
  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
        RISK_STYLES[level] || 'bg-ink-line text-ink/60'
      }`}
    >
      {level}
    </span>
  )
}

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-risk-low-soft text-risk-low',
  pending_approval: 'bg-risk-medium-soft text-risk-medium',
  rejected: 'bg-ink-line text-ink/60',
  failed: 'bg-risk-high-soft text-risk-high',
}

const STATUS_LABELS: Record<string, string> = {
  completed: 'Completed',
  pending_approval: 'Pending approval',
  rejected: 'Rejected',
  failed: 'Failed',
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
        STATUS_STYLES[status] || 'bg-ink-line text-ink/60'
      }`}
    >
      {STATUS_LABELS[status] || status}
    </span>
  )
}

export function TrustBadge({ trusted }: { trusted: boolean }) {
  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
        trusted ? 'bg-risk-low-soft text-risk-low' : 'bg-ink-line text-ink/60'
      }`}
    >
      {trusted ? 'Trusted' : 'Not trusted'}
    </span>
  )
}
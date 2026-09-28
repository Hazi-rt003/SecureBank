import { useEffect, useState } from 'react'
import * as api from '../api/resources'
import type { AuditLogEntry } from '../types'
import { PageHeader } from '../components/PageHeader'

const ACTION_LABELS: Record<string, string> = {
  register: 'Account created',
  login_success: 'Signed in',
  login_failed: 'Failed sign-in attempt',
  device_trusted: 'Device trusted',
  device_revoked: 'Device trust revoked',
  transaction_initiated: 'Transaction initiated',
  transaction_approved: 'Transaction approved',
  transaction_rejected: 'Transaction rejected',
}

export function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .listAuditLogs()
      .then(setLogs)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <PageHeader title="Audit log" subtitle="Security-relevant activity on your account" />

      <div className="px-10 py-8">
        {loading ? (
          <p className="text-sm text-ink/50">Loading…</p>
        ) : logs.length === 0 ? (
          <p className="text-sm text-ink/50 border border-dashed border-paper-line rounded-md px-4 py-6 text-center">
            No activity recorded yet.
          </p>
        ) : (
          <div className="border border-paper-line rounded-md divide-y divide-paper-line">
            {logs.map((entry) => (
              <div key={entry.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {ACTION_LABELS[entry.action] || entry.action}
                  </span>
                  <span className="text-xs text-ink/40 font-mono">
                    {entry.created_at ? new Date(entry.created_at).toLocaleString() : ''}
                  </span>
                </div>
                {entry.details && (
                  <div className="text-xs text-ink/50 mt-1 font-mono">{entry.details}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
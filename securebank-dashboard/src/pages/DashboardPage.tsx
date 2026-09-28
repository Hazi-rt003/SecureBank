import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as api from '../api/resources'
import type { Account, Transaction } from '../types'
import { PageHeader } from '../components/PageHeader'
import { RiskBadge } from '../components/Badges'

export function DashboardPage() {
  const [account, setAccount] = useState<Account | null>(null)
  const [pending, setPending] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getMyAccount(), api.listPendingTransactions()])
      .then(([acct, tx]) => {
        setAccount(acct)
        setPending(tx)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Your account at a glance"
        action={
          <Link
            to="/transactions"
            className="rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90 transition-colors"
          >
            Send money
          </Link>
        }
      />

      <div className="px-10 py-8">
        {loading ? (
          <p className="text-sm text-ink/50">Loading…</p>
        ) : (
          <>
            <div className="mb-10">
              <div className="text-sm text-ink/50 mb-1">
                {account?.account_number}
              </div>
              <div className="font-mono text-5xl font-medium tabular-nums tracking-tight">
                {account?.currency} {formatAmount(account?.balance)}
              </div>
            </div>

            <div>
              <h2 className="font-display text-base font-semibold mb-3">
                Awaiting your approval
              </h2>
              {pending.length === 0 ? (
                <p className="text-sm text-ink/50 border border-dashed border-paper-line rounded-md px-4 py-6 text-center">
                  Nothing pending. Transactions you initiate will need approval from a
                  trusted device before they complete.
                </p>
              ) : (
                <div className="border border-paper-line rounded-md divide-y divide-paper-line">
                  {pending.map((tx) => (
                    <div key={tx.id} className="px-4 py-3 flex items-center justify-between">
                      <div>
                        <div className="font-mono text-sm">
                          {tx.currency} {formatAmount(tx.amount)}
                        </div>
                        <div className="text-xs text-ink/50 mt-0.5">
                          {tx.created_at ? new Date(tx.created_at).toLocaleString() : ''}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <RiskBadge level={tx.risk_level} />
                        <Link
                          to="/transactions"
                          className="text-sm text-signal font-medium"
                        >
                          Review
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function formatAmount(value?: string) {
  if (!value) return '0.00'
  const n = Number(value)
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
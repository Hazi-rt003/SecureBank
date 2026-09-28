import { useEffect, useState, type FormEvent } from 'react'
import * as api from '../api/resources'
import type { Transaction } from '../types'
import { PageHeader } from '../components/PageHeader'
import { RiskBadge, StatusBadge } from '../components/Badges'
import { ApiError } from '../api/client'

export function TransactionsPage() {
  const [pending, setPending] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [actioningId, setActioningId] = useState<number | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  function refresh() {
    setLoading(true)
    api
      .listPendingTransactions()
      .then(setPending)
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleSend(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)
    try {
      await api.initiateTransaction(recipient, amount)
      setRecipient('')
      setAmount('')
      refresh()
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not send. Try again.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleApprove(id: number) {
    setActionError(null)
    setActioningId(id)
    try {
      await api.approveTransaction(id)
      refresh()
    } catch (err) {
      setActionError(
        err instanceof ApiError
          ? err.message
          : 'Could not approve this transaction.',
      )
    } finally {
      setActioningId(null)
    }
  }

  async function handleReject(id: number) {
    setActionError(null)
    setActioningId(id)
    try {
      await api.rejectTransaction(id)
      refresh()
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : 'Could not reject this transaction.',
      )
    } finally {
      setActioningId(null)
    }
  }

  return (
    <div>
      <PageHeader title="Transactions" subtitle="Send money and approve pending transfers" />

      <div className="px-10 py-8 grid grid-cols-[minmax(0,1fr)_320px] gap-10">
        <div>
          <h2 className="font-display text-base font-semibold mb-3">Pending approval</h2>

          {actionError && (
            <div className="mb-3 rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
              {actionError}
            </div>
          )}

          {loading ? (
            <p className="text-sm text-ink/50">Loading…</p>
          ) : pending.length === 0 ? (
            <p className="text-sm text-ink/50 border border-dashed border-paper-line rounded-md px-4 py-6 text-center">
              No transactions waiting on you right now.
            </p>
          ) : (
            <div className="border border-paper-line rounded-md divide-y divide-paper-line">
              {pending.map((tx) => (
                <div key={tx.id} className="px-4 py-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-mono text-lg tabular-nums">
                        {tx.currency} {formatAmount(tx.amount)}
                      </div>
                      <div className="text-xs text-ink/50 mt-1">
                        To account #{tx.recipient_account_id} ·{' '}
                        {tx.created_at ? new Date(tx.created_at).toLocaleString() : ''}
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <RiskBadge level={tx.risk_level} />
                        <StatusBadge status={tx.status} />
                      </div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button
                        onClick={() => handleReject(tx.id)}
                        disabled={actioningId === tx.id}
                        className="rounded-md border border-paper-line px-3 py-1.5 text-sm font-medium text-ink/70 hover:bg-paper-line/40 transition-colors disabled:opacity-50"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprove(tx.id)}
                        disabled={actioningId === tx.id}
                        className="rounded-md bg-signal px-3 py-1.5 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-50"
                      >
                        {actioningId === tx.id ? 'Working…' : 'Approve'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          <p className="mt-3 text-xs text-ink/40">
            Approving requires this device to be trusted. Register and trust this device
            from the Devices page first if approval fails.
          </p>
        </div>

        <div>
          <h2 className="font-display text-base font-semibold mb-3">Send money</h2>
          <form
            onSubmit={handleSend}
            className="border border-paper-line rounded-md p-4 flex flex-col gap-3"
          >
            <div>
              <label className="block text-sm font-medium mb-1.5">Recipient account</label>
              <input
                required
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="SB1234567890"
                className="w-full rounded-md border border-paper-line px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-signal"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Amount</label>
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full rounded-md border border-paper-line px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-signal"
              />
            </div>

            {formError && (
              <div className="rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
                {formError}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="mt-1 w-full rounded-md bg-signal py-2 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-60"
            >
              {submitting ? 'Sending…' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

function formatAmount(value: string) {
  const n = Number(value)
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
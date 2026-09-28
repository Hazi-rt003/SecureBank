import { useEffect, useState } from 'react'
import * as api from '../api/resources'
import type { Session } from '../types'
import { PageHeader } from '../components/PageHeader'
import { ApiError } from '../api/client'

export function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<number | 'others' | null>(null)
  const [error, setError] = useState<string | null>(null)

  function refresh() {
    setLoading(true)
    api
      .listSessions()
      .then(setSessions)
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleRevoke(id: number) {
    setError(null)
    setBusyId(id)
    try {
      await api.revokeSession(id)
      refresh()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not revoke that session.')
    } finally {
      setBusyId(null)
    }
  }

  async function handleRevokeOthers() {
    setError(null)
    setBusyId('others')
    try {
      await api.revokeOtherSessions()
      refresh()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not revoke other sessions.')
    } finally {
      setBusyId(null)
    }
  }

  const active = sessions.filter((s) => !s.revoked_at)

  return (
    <div>
      <PageHeader
        title="Sessions"
        subtitle="Everywhere you're currently signed in"
        action={
          active.length > 1 && (
            <button
              onClick={handleRevokeOthers}
              disabled={busyId === 'others'}
              className="rounded-md border border-paper-line px-4 py-2 text-sm font-medium text-ink/70 hover:bg-paper-line/40 transition-colors disabled:opacity-60"
            >
              {busyId === 'others' ? 'Working…' : 'Log out other devices'}
            </button>
          )
        }
      />

      <div className="px-10 py-8">
        {error && (
          <div className="mb-4 rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-sm text-ink/50">Loading…</p>
        ) : (
          <div className="border border-paper-line rounded-md divide-y divide-paper-line">
            {sessions.map((s) => (
              <div key={s.id} className="px-4 py-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium flex items-center gap-2">
                    Session #{s.id}
                    {s.is_current && (
                      <span className="text-xs text-signal font-normal">This session</span>
                    )}
                    {s.revoked_at && (
                      <span className="text-xs text-ink/40 font-normal">Revoked</span>
                    )}
                  </div>
                  <div className="text-xs text-ink/50 mt-0.5 font-mono">
                    Started {s.created_at ? new Date(s.created_at).toLocaleString() : '—'} ·
                    {' '}Expires {new Date(s.expires_at).toLocaleString()}
                  </div>
                </div>
                {!s.revoked_at && !s.is_current && (
                  <button
                    onClick={() => handleRevoke(s.id)}
                    disabled={busyId === s.id}
                    className="rounded-md border border-paper-line px-3 py-1.5 text-sm font-medium text-ink/70 hover:bg-paper-line/40 transition-colors disabled:opacity-50"
                  >
                    {busyId === s.id ? 'Working…' : 'Revoke'}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
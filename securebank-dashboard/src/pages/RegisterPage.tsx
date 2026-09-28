import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import * as authApi from '../api/auth'
import { ApiError } from '../api/client'

export function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await authApi.register(form)
      navigate('/login', { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Registration failed. Try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="font-display text-2xl font-semibold text-paper tracking-tight">
            SecureBank
          </span>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-paper rounded-lg px-8 py-8 flex flex-col gap-4"
        >
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Full name</label>
            <input
              required
              value={form.full_name}
              onChange={update('full_name')}
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={update('email')}
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Phone number</label>
            <input
              required
              value={form.phone_number}
              onChange={update('phone_number')}
              placeholder="+254700000000"
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={update('password')}
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
            />
          </div>

          {error && (
            <div className="rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="mt-2 w-full rounded-md bg-signal py-2.5 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-60"
          >
            {submitting ? 'Creating account…' : 'Create account'}
          </button>

          <p className="text-center text-sm text-ink/60 mt-1">
            Already have an account?{' '}
            <Link to="/login" className="text-signal font-medium">
              Log in
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
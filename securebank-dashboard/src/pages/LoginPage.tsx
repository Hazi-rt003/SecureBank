import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth, ApiError } from '../auth/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [step, setStep] = useState<'idle' | 'passkey'>('idle')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      setStep('idle')
      // login() internally detects step-up and prompts for a passkey; we
      // just show a different status message while that's in flight.
      const loginPromise = login(email, password)
      setStep('passkey')
      await loginPromise
      navigate('/', { replace: true })
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Something went wrong. Try again.')
      }
    } finally {
      setSubmitting(false)
      setStep('idle')
    }
  }

  return (
    <div className="min-h-screen bg-ink flex items-center justify-center px-4">
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
            <label className="block text-sm font-medium text-ink mb-1.5" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
              autoComplete="email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-ink mb-1.5" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-paper-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
              {error}
            </div>
          )}

          {step === 'passkey' && (
            <div className="rounded-md bg-signal-soft px-3 py-2 text-sm text-signal">
              This device has a passkey on file — confirm with your browser or security key
              to finish signing in.
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="mt-2 w-full rounded-md bg-signal py-2.5 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-60"
          >
            {submitting ? 'Signing in…' : 'Log in'}
          </button>

          <p className="text-center text-sm text-ink/60 mt-1">
            Don't have an account?{' '}
            <Link to="/register" className="text-signal font-medium">
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
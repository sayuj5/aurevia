import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShieldCheck } from 'lucide-react'
import { useAuth } from '../lib/auth'

export function PatientLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Enter your email and password to continue.')
      return
    }

    const normalizedEmail = email.trim().toLowerCase()
    let role: 'counselor' | 'police' | 'admin' | 'citizen' = 'citizen'

    if (normalizedEmail === 's.kulkarni@aurevia.org') role = 'counselor'
    else if (normalizedEmail === 'r.singh@aurevia.org') role = 'police'
    else if (normalizedEmail === 'p.joshi@aurevia.org') role = 'admin'

    // Placeholder for POST /api/v1/auth/login — issues a JWT per the
    // OAuth2 + JWT spec in the backend docs. Swap this in once live.
    login(normalizedEmail, role)

    if (role === 'citizen') {
      navigate('/assessment', { replace: true })
      return
    }

    const requestedPath = (location.state as { from?: string } | null)?.from
    const redirectTo = requestedPath?.startsWith('/dashboard') || requestedPath?.startsWith('/admin') ? requestedPath : '/dashboard'
    navigate(redirectTo, { replace: true })
  }

  return (
    <div className="min-h-screen bg-[var(--color-paper)] flex flex-col items-center justify-center px-6">
      <Link to="/" className="absolute top-6 left-6 flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]">
        <ArrowLeft className="w-4 h-4" /> Back
      </Link>

      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <ShieldCheck className="w-6 h-6 text-[var(--color-sage)]" />
          <span className="font-display text-xl">Welcome back</span>
        </div>

        <form onSubmit={handleSubmit} className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-6 flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-xl border border-[var(--color-border)] bg-white px-4 py-2.5 text-sm focus:border-[var(--color-sage)] outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-xl border border-[var(--color-border)] bg-white px-4 py-2.5 text-sm focus:border-[var(--color-sage)] outline-none"
            />
          </div>

          {error && <p className="text-xs text-[var(--color-brick)]">{error}</p>}

          <button
            type="submit"
            className="bg-[var(--color-ink)] text-white py-2.5 rounded-full text-sm font-medium hover:bg-[var(--color-sage)] transition-colors mt-2"
          >
            Sign in
          </button>

          <p className="text-center text-xs text-[var(--color-ink-soft)]">
            First time here?{' '}
            <Link to="/register" className="text-[var(--color-sage)] font-medium">
              Create an account
            </Link>
          </p>
        </form>

        <p className="text-center text-xs text-[var(--color-ink-soft)] mt-6">
          Your account is used only to protect your check-in history. It's
          never shared or shown to anyone outside your support team.
        </p>
      </div>
    </div>
  )
}
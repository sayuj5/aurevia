import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShieldCheck } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'

export function PatientLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  // ProtectedRoute passes the page a staff member was trying to reach via
  // location state; citizens arriving straight from Landing have no state,
  // so they fall through to the assessment flow as before.
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Enter your email and password to continue.')
      return
    }
    // Placeholder for POST /api/v1/auth/login — issues a JWT per the
    // OAuth2 + JWT spec in the backend docs. Swap this in once live.
    const authenticatedUser = login(email, password)
    const requestedPath = (location.state as { from?: string } | null)?.from
    const redirectTo = authenticatedUser.role === 'citizen' ? '/assessment' : requestedPath?.startsWith('/dashboard') ? requestedPath : '/dashboard'
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
            <Label htmlFor="login-email">Email</Label>
            <Input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div>
            <Label htmlFor="login-password">Password</Label>
            <Input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-xs text-[var(--color-brick)]">{error}</p>}

          <Button type="submit" className="mt-2">Sign in</Button>

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

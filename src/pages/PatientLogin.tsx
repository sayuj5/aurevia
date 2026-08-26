import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShieldCheck } from 'lucide-react'
import { useStore } from '../store/useStore'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

export function PatientLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const login = useStore((state) => state.login)
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) {
      setError('Enter your email to continue.')
      return
    }

    const normalizedEmail = email.trim().toLowerCase()
    let role: 'counselor' | 'police' | 'citizen' = 'citizen'

    if (normalizedEmail === 's.kulkarni@aurevia.org') role = 'counselor'
    else if (normalizedEmail === 'r.singh@aurevia.org') role = 'police'

    login(normalizedEmail, role)

    if (role === 'citizen') {
      navigate('/assessment', { replace: true })
      return
    }

    navigate('/dashboard', { replace: true })
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_15%_20%,rgba(170,200,178,0.28),transparent_45%),radial-gradient(circle_at_85%_10%,rgba(168,132,120,0.2),transparent_35%),linear-gradient(180deg,#f7f2ec_0%,#efe7de_100%)] flex flex-col items-center justify-center px-6 py-12">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.25)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.25)_1px,transparent_1px)] bg-[size:34px_34px] opacity-45" />

      <Link to="/" className="absolute top-6 left-6 z-10 flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]">
        <ArrowLeft className="w-4 h-4" /> Back
      </Link>

      <Card className="relative z-10 w-full max-w-md border-white/70 bg-white/80 shadow-[0_24px_80px_rgba(52,37,28,0.12)] backdrop-blur-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2 justify-center">
            <ShieldCheck className="w-6 h-6 text-[var(--color-sage)]" />
            <span className="font-display text-xl">Welcome back</span>
          </div>
          <CardTitle className="pt-3 text-center text-xs tracking-[0.12em] uppercase text-[var(--color-ink-soft)]/90">
            Secure patient portal access
          </CardTitle>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="login-email">Email</Label>
              <Input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
            <div className="space-y-1.5">
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
        </CardContent>
      </Card>

    </div>
  )
}

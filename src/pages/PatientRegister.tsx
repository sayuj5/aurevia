import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShieldCheck } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'

export function PatientRegister() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.password) {
      setError('Fill in every field to create your account.')
      return
    }
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    // Placeholder for POST /api/v1/auth/register — creates the account and
    // issues a JWT per the OAuth2 + JWT spec in the backend docs.
    login(form.email, form.password)
    navigate('/assessment')
  }

  return (
    <div className="min-h-screen bg-[var(--color-paper)] flex flex-col items-center justify-center px-6">
      <Link to="/login" className="absolute top-6 left-6 flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]">
        <ArrowLeft className="w-4 h-4" /> Back to sign in
      </Link>

      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <ShieldCheck className="w-6 h-6 text-[var(--color-sage)]" />
          <span className="font-display text-xl">Create your account</span>
        </div>

        <form onSubmit={handleSubmit} className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-6 flex flex-col gap-4">
          <div>
            <Label htmlFor="reg-name">Name</Label>
            <Input
              id="reg-name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="reg-email">Email</Label>
            <Input
              id="reg-email"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="reg-password">Password</Label>
            <Input
              id="reg-password"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="reg-confirm">Confirm password</Label>
            <Input
              id="reg-confirm"
              type="password"
              value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })}
            />
          </div>

          {error && <p className="text-xs text-[var(--color-brick)]">{error}</p>}

          <Button type="submit" className="mt-2">Create account</Button>
        </form>

        <p className="text-center text-xs text-[var(--color-ink-soft)] mt-6">
          Your information is encrypted and seen only by your assigned support team.
        </p>
      </div>
    </div>
  )
}

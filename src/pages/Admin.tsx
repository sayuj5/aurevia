import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { mockUsers, type AppUser } from '../data/mockUsers'

export function Admin() {
  const [users, setUsers] = useState<AppUser[]>(mockUsers)

  const toggleStatus = (id: string) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, status: u.status === 'active' ? 'suspended' : 'active' } : u))
    )
  }

  return (
    <div className="p-6 md:p-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl">Admin</h1>
          <p className="text-sm text-[var(--color-ink-soft)]">Manage staff accounts, roles, and access.</p>
        </div>
        <button className="flex items-center gap-2 bg-[var(--color-ink)] text-white px-4 py-2.5 rounded-full text-sm font-medium hover:bg-[var(--color-sage)] transition-colors">
          <UserPlus className="w-4 h-4" /> Invite staff
        </button>
      </div>

      <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] text-left text-xs text-[var(--color-ink-soft)] uppercase tracking-wide">
              <th className="px-5 py-3 font-medium">Name</th>
              <th className="px-5 py-3 font-medium">Email</th>
              <th className="px-5 py-3 font-medium">Role</th>
              <th className="px-5 py-3 font-medium">District</th>
              <th className="px-5 py-3 font-medium">Caseload</th>
              <th className="px-5 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-[var(--color-border)] last:border-0">
                <td className="px-5 py-3 font-medium">{u.name}</td>
                <td className="px-5 py-3 text-[var(--color-ink-soft)]">{u.email}</td>
                <td className="px-5 py-3">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-sage)]/15 text-[var(--color-sage)] font-medium">
                    {u.role}
                  </span>
                </td>
                <td className="px-5 py-3 text-[var(--color-ink-soft)]">{u.district}</td>
                <td className="px-5 py-3 font-mono">{u.caseload}</td>
                <td className="px-5 py-3">
                  <button
                    onClick={() => toggleStatus(u.id)}
                    className={`text-xs font-medium px-2.5 py-1 rounded-full transition-colors ${
                      u.status === 'active'
                        ? 'bg-[var(--color-sage)]/15 text-[var(--color-sage)] hover:bg-[var(--color-brick)]/15 hover:text-[var(--color-brick)]'
                        : 'bg-[var(--color-brick)]/15 text-[var(--color-brick)] hover:bg-[var(--color-sage)]/15 hover:text-[var(--color-sage)]'
                    }`}
                  >
                    {u.status === 'active' ? 'Active' : 'Suspended'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

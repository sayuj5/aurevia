import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { FileText } from 'lucide-react'
import { fetchCases, tierMeta, type CaseRecord } from '../api/cases'
import { mockUsers } from '../data/mockUsers'
import { useStore } from '../store/useStore'

const statusMeta: Record<CaseRecord['status'], { label: string; className: string }> = {
  open: { label: 'Open', className: 'bg-[var(--color-terracotta)]/15 text-[var(--color-terracotta)]' },
  in_review: { label: 'In review', className: 'bg-[var(--color-sage)]/15 text-[var(--color-sage)]' },
  closed: { label: 'Closed', className: 'bg-[var(--color-ink-soft)]/15 text-[var(--color-ink-soft)]' },
}

export function CaseManagement() {
  const { data } = useQuery({ queryKey: ['cases'], queryFn: fetchCases })

  // Same shared store the Dashboard reads from — editing status/assignee
  // here is immediately visible on the Dashboard too, and vice versa.
  const cases = useStore((s) => s.cases)
  const setCases = useStore((s) => s.setCases)
  const updateStatus = useStore((s) => s.updateCaseStatus)
  const updateAssignee = useStore((s) => s.updateCaseAssignee)

  useEffect(() => {
    if (data) setCases(data)
  }, [data, setCases])

  const counsellors = mockUsers.filter((u) => u.role !== 'Admin')

  return (
    <div className="p-6 md:p-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl">Case Management</h1>
          <p className="text-sm text-[var(--color-ink-soft)]">Assign, update status, and track every open case.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] text-left text-xs text-[var(--color-ink-soft)] uppercase tracking-wide">
              <th className="px-5 py-3 font-medium">Case</th>
              <th className="px-5 py-3 font-medium">Tier</th>
              <th className="px-5 py-3 font-medium">District</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium">Assigned to</th>
              <th className="px-5 py-3 font-medium">Report</th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.id} className="border-b border-[var(--color-border)] last:border-0">
                <td className="px-5 py-3 font-mono">{c.code}</td>
                <td className="px-5 py-3">
                  <span
                    className="text-xs font-medium px-2 py-0.5 rounded-full text-white"
                    style={{ backgroundColor: tierMeta[c.tier].color }}
                  >
                    {tierMeta[c.tier].label}
                  </span>
                </td>
                <td className="px-5 py-3 text-[var(--color-ink-soft)]">{c.district}</td>
                <td className="px-5 py-3">
                  <select
                    value={c.status}
                    onChange={(e) => updateStatus(c.id, e.target.value as CaseRecord['status'])}
                    className={`text-xs font-medium rounded-full px-2.5 py-1 border-0 outline-none cursor-pointer ${statusMeta[c.status].className}`}
                  >
                    <option value="open">Open</option>
                    <option value="in_review">In review</option>
                    <option value="closed">Closed</option>
                  </select>
                </td>
                <td className="px-5 py-3">
                  <select
                    value={c.assignedTo ?? ''}
                    onChange={(e) => updateAssignee(c.id, e.target.value)}
                    className="text-xs rounded-lg border border-[var(--color-border)] bg-white px-2 py-1 outline-none focus:border-[var(--color-sage)]"
                  >
                    <option value="">Unassigned</option>
                    {counsellors.map((u) => (
                      <option key={u.id} value={u.name}>{u.name}</option>
                    ))}
                  </select>
                </td>
                <td className="px-5 py-3">
                  <Link
                    to={`/cases/${c.id}/report`}
                    className="flex items-center gap-1.5 text-xs text-[var(--color-sage)] hover:text-[var(--color-ink)] font-medium"
                  >
                    <FileText className="w-3.5 h-3.5" /> View report
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

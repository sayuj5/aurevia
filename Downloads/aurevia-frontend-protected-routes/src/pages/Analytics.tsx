import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts'
import { mockCases, tierMeta } from '../data/mockCases'

const tierCounts = (['critical', 'high', 'moderate', 'low'] as const).map((t) => ({
  tier: tierMeta[t].label,
  count: mockCases.filter((c) => c.tier === t).length,
  color: tierMeta[t].color,
}))

const districtCounts = Object.entries(
  mockCases.reduce<Record<string, number>>((acc, c) => {
    acc[c.district] = (acc[c.district] ?? 0) + 1
    return acc
  }, {})
).map(([district, count]) => ({ district, count }))

const monthlyTrend = [
  { month: 'Mar', avgScore: 41 },
  { month: 'Apr', avgScore: 46 },
  { month: 'May', avgScore: 44 },
  { month: 'Jun', avgScore: 52 },
  { month: 'Jul', avgScore: 58 },
  { month: 'Aug', avgScore: 61 },
]

export function Analytics() {
  const avgScore = Math.round(mockCases.reduce((s, c) => s + c.score, 0) / mockCases.length)
  const criticalCount = mockCases.filter((c) => c.tier === 'critical').length

  return (
    <div className="p-6 md:p-10">
      <h1 className="font-display text-2xl mb-1">Analytics</h1>
      <p className="text-sm text-[var(--color-ink-soft)] mb-6">Aggregate trends across all active cases.</p>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
          <p className="text-xs text-[var(--color-ink-soft)] mb-1">Active cases</p>
          <p className="font-mono text-3xl font-medium">{mockCases.length}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
          <p className="text-xs text-[var(--color-ink-soft)] mb-1">Average risk score</p>
          <p className="font-mono text-3xl font-medium">{avgScore}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
          <p className="text-xs text-[var(--color-ink-soft)] mb-1">Critical cases</p>
          <p className="font-mono text-3xl font-medium text-[var(--color-brick)]">{criticalCount}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
          <h3 className="text-sm font-medium mb-4 text-[var(--color-ink-soft)]">Cases by tier</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={tierCounts} dataKey="count" nameKey="tier" innerRadius={55} outerRadius={85} paddingAngle={3}>
                {tierCounts.map((entry) => (
                  <Cell key={entry.tier} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: 'var(--color-paper)', border: '1px solid var(--color-border)', borderRadius: 12, fontSize: 13 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-3 justify-center mt-2">
            {tierCounts.map((t) => (
              <span key={t.tier} className="flex items-center gap-1.5 text-xs text-[var(--color-ink-soft)]">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: t.color }} />
                {t.tier} ({t.count})
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
          <h3 className="text-sm font-medium mb-4 text-[var(--color-ink-soft)]">Cases by district</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={districtCounts}>
              <CartesianGrid stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="district" stroke="var(--color-ink-soft)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--color-ink-soft)" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ background: 'var(--color-paper)', border: '1px solid var(--color-border)', borderRadius: 12, fontSize: 13 }} />
              <Bar dataKey="count" fill="var(--color-sage)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
        <h3 className="text-sm font-medium mb-4 text-[var(--color-ink-soft)]">Average risk score — 6 months</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={monthlyTrend}>
            <CartesianGrid stroke="var(--color-border)" vertical={false} />
            <XAxis dataKey="month" stroke="var(--color-ink-soft)" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--color-ink-soft)" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip contentStyle={{ background: 'var(--color-paper)', border: '1px solid var(--color-border)', borderRadius: 12, fontSize: 13 }} />
            <Line type="monotone" dataKey="avgScore" stroke="var(--color-terracotta)" strokeWidth={2.5} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

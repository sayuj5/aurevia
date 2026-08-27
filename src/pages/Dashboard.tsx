import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, TrendingUp, TrendingDown, Minus, MapPin, Languages, Bell, Circle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { fetchCases, tierMeta, type Tier } from '../api/cases'
import { TideLine } from '../components/TideLine'
import { useTriageWebSocket } from '../hooks/useTriageWebSocket'
import { useStore } from '../store/useStore'

const trendHistory = [
  { t: 'Mon', score: 38 },
  { t: 'Tue', score: 45 },
  { t: 'Wed', score: 52 },
  { t: 'Thu', score: 61 },
  { t: 'Fri', score: 74 },
  { t: 'Sat', score: 83 },
  { t: 'Today', score: 91 },
]

const TrendIcon = { rising: TrendingUp, falling: TrendingDown, flat: Minus }

export function Dashboard() {
  const liveStatus = useTriageWebSocket()
  const [filter, setFilter] = useState<Tier | 'all'>('all')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  // TanStack Query owns the initial fetch (placeholder for GET /api/v1/distress/cases).
  const { data, isLoading, isError } = useQuery({
    queryKey: ['cases'],
    queryFn: fetchCases,
  })

  // The Zustand store is the single shared source of truth after that —
  // Case Management reads/writes the same `cases` array, so edits made
  // there (status, assignee) show up here too, and vice versa.
  const cases = useStore((s) => s.cases)
  const setCases = useStore((s) => s.setCases)

  useEffect(() => {
    if (data) setCases(data)
  }, [data, setCases])

  const filtered = filter === 'all' ? cases : cases.filter((c) => c.tier === filter)
  const selected = cases.find((c) => c.id === selectedId) ?? cases[0]
  const alertCount = cases.filter((c) => c.awaitingReview).length

  if (isLoading || cases.length === 0) {
    return (
      <div className="min-h-screen bg-[var(--color-paper)] flex items-center justify-center">
        <p className="text-sm text-[var(--color-ink-soft)]">Loading case queue...</p>
      </div>
    )
  }

  if (isError || !selected) {
    return (
      <div className="min-h-screen bg-[var(--color-paper)] flex items-center justify-center">
        <p className="text-sm text-[var(--color-brick)]">Unable to load the case queue.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-paper)]">
      <header className="border-b border-[var(--color-border)] px-6 md:px-10 py-4 flex items-center justify-between bg-white/60 backdrop-blur sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-[var(--color-ink-soft)] hover:text-[var(--color-ink)]">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <span className="font-display text-lg">Case Triage Queue</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 text-xs text-[var(--color-ink-soft)]">
            <Circle
              className={`w-2 h-2 ${
                liveStatus === 'live'
                  ? 'fill-[var(--color-sage)] text-[var(--color-sage)]'
                  : 'fill-[var(--color-ink-soft)] text-[var(--color-ink-soft)]'
              }`}
            />
            {liveStatus === 'live' ? 'Live' : liveStatus === 'connecting' ? 'Connecting…' : 'Offline — showing cached data'}
          </span>
          <div className="flex items-center gap-2 text-sm font-medium text-[var(--color-brick)]">
            <Bell className="w-4 h-4" />
            {alertCount} awaiting review
          </div>
        </div>
      </header>

      <div className="grid lg:grid-cols-[380px_1fr] gap-0 lg:h-[calc(100vh-65px)]">
        <div className="border-r border-[var(--color-border)] flex flex-col overflow-hidden">
          <div className="flex gap-1 p-3 border-b border-[var(--color-border)] overflow-x-auto">
            {(['all', 'critical', 'high', 'moderate', 'low'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setFilter(t)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                  filter === t
                    ? 'bg-[var(--color-ink)] text-white'
                    : 'bg-white text-[var(--color-ink-soft)] hover:bg-[var(--color-paper-dim)]'
                }`}
              >
                {t === 'all' ? 'All cases' : tierMeta[t].label}
              </button>
            ))}
          </div>

          <div className="overflow-y-auto flex-1">
            {filtered
              .slice()
              .sort((a, b) => b.score - a.score)
              .map((c) => {
                const Icon = TrendIcon[c.trend]
                return (
                  <button
                    key={c.id}
                    onClick={() => setSelectedId(c.id)}
                    className={`w-full text-left p-4 border-b border-[var(--color-border)] transition-colors ${
                      selectedId === c.id ? 'bg-white' : 'hover:bg-white/60'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-sm font-medium">{c.code}</span>
                      <div className="flex items-center gap-1 text-xs text-[var(--color-ink-soft)]">
                        <Icon className="w-3.5 h-3.5" />
                        {c.lastUpdate}
                      </div>
                    </div>
                    <TideLine score={c.score} tier={c.tier} size="sm" />
                    <p className="text-xs text-[var(--color-ink-soft)] mt-2 line-clamp-1">{c.summary}</p>
                  </button>
                )
              })}
          </div>
        </div>

        <div className="overflow-y-auto p-6 md:p-10">
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-display text-2xl">{selected.code}</span>
                <span
                  className="text-xs font-medium px-2 py-0.5 rounded-full text-white"
                  style={{ backgroundColor: tierMeta[selected.tier].color }}
                >
                  {tierMeta[selected.tier].label}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-[var(--color-ink-soft)]">
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {selected.district}</span>
                <span className="flex items-center gap-1"><Languages className="w-3.5 h-3.5" /> {selected.language}</span>
              </div>
            </div>
            {selected.awaitingReview && (
              <button className="bg-[var(--color-ink)] text-white px-5 py-2.5 rounded-full text-sm font-medium hover:bg-[var(--color-sage)] transition-colors">
                Acknowledge & respond
              </button>
            )}
          </div>

          <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5 mb-6">
            <h3 className="text-sm font-medium mb-3 text-[var(--color-ink-soft)]">Latest note</h3>
            <p className="text-[var(--color-ink)] leading-relaxed">{selected.summary}</p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {(['nlp', 'vocal', 'caseHistory'] as const).map((key) => (
              <div key={key} className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-4">
                <p className="text-xs text-[var(--color-ink-soft)] mb-2 capitalize">
                  {key === 'nlp' ? 'Text / NLP signal' : key === 'vocal' ? 'Vocal biomarker signal' : 'Case history signal'}
                </p>
                <p className="font-mono text-2xl font-medium">{Math.round(selected.signals[key] * 100)}</p>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-5">
            <h3 className="text-sm font-medium mb-4 text-[var(--color-ink-soft)]">Risk trajectory — 7 days</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trendHistory}>
                <CartesianGrid stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="t" stroke="var(--color-ink-soft)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--color-ink-soft)" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    background: 'var(--color-paper)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 12,
                    fontSize: 13,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="var(--color-brick)"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: 'var(--color-brick)' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

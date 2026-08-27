import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Sparkles } from 'lucide-react'
import { tierMeta } from '../data/mockCases'
import { useStore } from '../store/useStore'

export function ReportView() {
  const { id } = useParams()
  // Reads from the same shared store as Dashboard/Case Management, so a
  // live score update or status change is reflected here too.
  const cases = useStore((s) => s.cases)
  const c = cases.find((c) => c.id === id) ?? cases[0]

  if (!c) {
    return <div className="p-10 text-sm text-[var(--color-ink-soft)]">Loading report…</div>
  }
  const maxContribution = Math.max(...c.featureAttribution.map((f) => f.contribution))

  return (
    <div className="p-6 md:p-10 max-w-3xl">
      <Link to="/cases" className="inline-flex items-center gap-2 text-sm text-[var(--color-ink-soft)] hover:text-[var(--color-ink)] mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to case management
      </Link>

      <div className="flex items-center gap-2 mb-1">
        <Sparkles className="w-5 h-5 text-[var(--color-sage)]" />
        <h1 className="font-display text-2xl">AI-Generated Risk Report</h1>
      </div>
      <p className="text-sm text-[var(--color-ink-soft)] mb-6">
        Case {c.code} · Generated from the Dynamic Risk Fusion Engine
      </p>

      <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <span className="font-mono text-3xl font-medium">{c.score}<span className="text-base text-[var(--color-ink-soft)]">/100</span></span>
          <span
            className="text-xs font-medium px-3 py-1 rounded-full text-white"
            style={{ backgroundColor: tierMeta[c.tier].color }}
          >
            {tierMeta[c.tier].label} risk
          </span>
        </div>
        <p className="text-sm text-[var(--color-ink-soft)] leading-relaxed">
          This score combines text sentiment, vocal biomarkers, and case history using
          weighted fusion. A safety override raises any case to Critical automatically
          if a single signal exceeds 0.85, regardless of the combined average.
        </p>
      </div>

      <div className="rounded-2xl border border-[var(--color-border)] bg-white/60 p-6">
        <h2 className="text-sm font-medium mb-1">Why this score — feature attribution</h2>
        <p className="text-xs text-[var(--color-ink-soft)] mb-5">
          Ranked by contribution to the final risk score (SHAP values).
        </p>

        <div className="flex flex-col gap-4">
          {c.featureAttribution
            .sort((a, b) => b.contribution - a.contribution)
            .map((f) => (
              <div key={f.feature}>
                <div className="flex items-baseline justify-between mb-1.5">
                  <span className="text-sm">{f.feature}</span>
                  <span className="font-mono text-xs text-[var(--color-ink-soft)]">
                    +{Math.round(f.contribution * 100)}%
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-[var(--color-paper-dim)] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[var(--color-sage)]"
                    style={{ width: `${(f.contribution / maxContribution) * 100}%` }}
                  />
                </div>
              </div>
            ))}
        </div>
      </div>

      <p className="text-xs text-[var(--color-ink-soft)] mt-6">
        This report supports a counsellor's judgment. It does not replace one — always
        corroborate with a direct check-in before acting on an automated score alone.
      </p>
    </div>
  )
}

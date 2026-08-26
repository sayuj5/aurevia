import { tierMeta, type Tier } from '../data/mockCases'

interface TideLineProps {
  score: number
  tier: Tier
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export function TideLine({ score, tier, size = 'md', showLabel = true }: TideLineProps) {
  const meta = tierMeta[tier]
  const height = size === 'sm' ? 'h-1.5' : size === 'lg' ? 'h-3' : 'h-2'

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-baseline justify-between mb-1.5">
          <span
            className="font-body text-sm font-medium"
            style={{ color: meta.color }}
          >
            {meta.label}
          </span>
          <span className="font-mono text-xs text-[var(--color-ink-soft)]">
            {score}/100
          </span>
        </div>
      )}
      <div className={`w-full ${height} rounded-full bg-[var(--color-paper-dim)] overflow-hidden relative`}>
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${score}%`,
            background: `linear-gradient(90deg, ${meta.color}99, ${meta.color})`,
          }}
        />
      </div>
    </div>
  )
}

import { Send, MessageCircle, Smartphone, Mail } from 'lucide-react'
import { tierMeta } from '../data/mockCases'
import { useStore } from '../store/useStore'

const channelIcon = { websocket: Send, telegram: MessageCircle, fcm: Smartphone, email: Mail }
const channelLabel = { websocket: 'Live dashboard', telegram: 'Telegram', fcm: 'Push notification', email: 'Email' }

export function Notifications() {
  // Same store the sidebar badge (AppShell) reads its unread count from —
  // previously this page held its own separate copy, so the badge was
  // always stuck at 0 no matter what showed here. Seeding happens once in
  // AppShell, since that mounts for every protected page, not just this one.
  const items = useStore((s) => s.notifications)
  const markAllRead = useStore((s) => s.markAllNotificationsRead)

  const unreadCount = items.filter((n) => !n.read).length

  return (
    <div className="p-6 md:p-10 max-w-2xl">
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-display text-2xl">Notifications</h1>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="text-xs text-[var(--color-sage)] font-medium hover:text-[var(--color-ink)]">
            Mark all as read
          </button>
        )}
      </div>
      <p className="text-sm text-[var(--color-ink-soft)] mb-6">
        Every alert dispatched by the Alert Engine, across all channels.
      </p>

      <div className="flex flex-col gap-3">
        {items.map((n) => {
          const Icon = channelIcon[n.channel]
          return (
            <div
              key={n.id}
              className={`rounded-2xl border p-4 flex gap-3 items-start transition-colors ${
                n.read ? 'border-[var(--color-border)] bg-white/40' : 'border-[var(--color-sage)]/40 bg-white'
              }`}
            >
              <div
                className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                style={{ backgroundColor: `${tierMeta[n.tier].color}22` }}
              >
                <Icon className="w-4 h-4" style={{ color: tierMeta[n.tier].color }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-sm font-medium">{n.caseCode}</span>
                  <span
                    className="text-[10px] font-medium px-1.5 py-0.5 rounded-full text-white"
                    style={{ backgroundColor: tierMeta[n.tier].color }}
                  >
                    {tierMeta[n.tier].label}
                  </span>
                  {!n.read && <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-sage)]" />}
                </div>
                <p className="text-sm text-[var(--color-ink)]">{n.message}</p>
                <p className="text-xs text-[var(--color-ink-soft)] mt-1">
                  {channelLabel[n.channel]} · {n.timestamp}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

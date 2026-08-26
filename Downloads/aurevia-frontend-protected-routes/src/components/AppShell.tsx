import { useEffect } from 'react'
import { useStore } from '../store/useStore';
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderKanban,
  BarChart3,
  Map,
  Bell,
  ShieldCheck,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../lib/auth'
import { mockNotifications } from '../data/mockUsers'
const NAV_ITEMS = [
  { to: '/dashboard', label: 'Triage Queue', icon: LayoutDashboard },
  { to: '/cases', label: 'Case Management', icon: FolderKanban },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/map', label: 'Incident Map', icon: Map },
  { to: '/notifications', label: 'Notifications', icon: Bell },
  { to: '/admin', label: 'Admin', icon: ShieldCheck },
]

export function AppShell() {
  const notifications = useStore((state) => state.notifications);
  const setNotifications = useStore((state) => state.setNotifications)
  const latestAlert = notifications[0];
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const unread = notifications.filter((n) => !n.read).length

  // Seed once here (not in Notifications.tsx) so the sidebar badge is
  // correct the moment a counsellor logs in, before they've even opened
  // the Notifications page.
  useEffect(() => {
    if (notifications.length === 0) setNotifications(mockNotifications)
  }, [notifications.length, setNotifications])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-[var(--color-paper)] flex">
      <aside className="w-60 shrink-0 border-r border-[var(--color-border)] bg-white/40 flex flex-col">
        <div className="px-5 py-6 flex items-center gap-2">
          <img src="/aurevia-logo.png" alt="Aurevia" className="h-16 w-auto object-contain" />
          {/* Real-time Glassmorphism Alert Toast */}
      {latestAlert && !latestAlert.read && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div className="bg-gray-900/60 backdrop-blur-md border border-gray-600/50 shadow-2xl text-white p-5 rounded-2xl">
            <div className="flex items-center gap-3">
              <span className="flex h-3 w-3 rounded-full bg-red-500"></span>
              <p className="font-bold text-red-400">Emergency Escalation</p>
            </div>
            <p className="text-sm mt-2 text-gray-200">
              {latestAlert.message || 'A new high-risk case requires immediate review.'}
            </p>
          </div>
        </div>
      )}
        </div>

        <nav className="flex-1 px-3 flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors relative ${
                  isActive
                    ? 'bg-[var(--color-ink)] text-white'
                    : 'text-[var(--color-ink-soft)] hover:bg-[var(--color-paper-dim)]'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
              {label === 'Notifications' && unread > 0 && (
                <span className="ml-auto bg-[var(--color-brick)] text-white text-[10px] font-semibold rounded-full w-4 h-4 flex items-center justify-center">
                  {unread}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-[var(--color-border)]">
          <p className="text-sm font-medium">{user?.name ?? 'Guest'}</p>
          <p className="text-xs text-[var(--color-ink-soft)] mb-3">{user?.role ?? ''}</p>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-xs text-[var(--color-ink-soft)] hover:text-[var(--color-brick)] transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" /> Sign out
          </button>
        </div>
      </aside>

      <div className="flex-1 min-w-0">
        <Outlet />
      </div>
    </div>
  )
}

import { Navigate, Outlet, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useStore } from '../store/useStore'

type AllowedRole = 'counselor' | 'police' | 'citizen'

interface ProtectedRouteProps {
  allowedRoles?: AllowedRole[]
  children?: ReactNode
}

// Gates every staff route (dashboard, cases, analytics, map, notifications,
// admin) behind the same /login screen used for the citizen check-in flow.
// No second login UI is added — per Bhumika's task card ("Protected routes")
// this just wires the existing session check in front of AppShell.
export function ProtectedRoute({ allowedRoles, children }: ProtectedRouteProps) {
  const user = useStore((state) => state.user)
  const isAuthenticated = useStore((state) => state.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (allowedRoles && (!user.role || !allowedRoles.includes(user.role))) {
    return <Navigate to={user.role === 'citizen' ? '/assessment' : '/dashboard'} replace />
  }

  return children ? <>{children}</> : <Outlet />
}

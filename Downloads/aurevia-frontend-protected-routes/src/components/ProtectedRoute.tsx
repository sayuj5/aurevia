import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'

// Gates every staff route (dashboard, cases, analytics, map, notifications,
// admin) behind the same /login screen used for the citizen check-in flow.
// No second login UI is added — per Bhumika's task card ("Protected routes")
// this just wires the existing session check in front of AppShell.
export function ProtectedRoute() {
  const { user, isAuthenticated } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (user.role !== 'counselor' && user.role !== 'police') {
    return <Navigate to="/assessment" replace />
  }

  return <Outlet />
}

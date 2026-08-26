import { useAuthStore, type AuthUser, type UserRole } from '../store/useAuthStore'
import type { ReactNode } from 'react'

export type { AuthUser, UserRole }

export function AuthProvider({ children }: { children: ReactNode }) {
  return children
}

export function useAuth() {
  const user = useAuthStore((state) => state.user)
  const login = useAuthStore((state) => state.login)
  const logout = useAuthStore((state) => state.logout)

  return { user, login, logout }
}

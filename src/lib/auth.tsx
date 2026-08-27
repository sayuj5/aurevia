import { useStore } from '../store/useStore'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return children
}

export function useAuth() {
  const user = useStore((state) => state.user)
  const login = useStore((state) => state.login)
  const logout = useStore((state) => state.logout)

  return { user, login, logout }
}
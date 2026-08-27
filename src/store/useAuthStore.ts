import { create } from 'zustand'
import { mockUsers } from '../data/mockUsers'

export type UserRole = 'counselor' | 'police' | 'citizen'

export interface AuthUser {
  name: string
  email: string
  role: UserRole
}

interface AuthState {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, password: string) => AuthUser
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: (email: string, _password: string) => {
    const staffUser = mockUsers.find((candidate) => candidate.email.toLowerCase() === email.toLowerCase())
    const role: UserRole = staffUser
      ? staffUser.role === 'Officer' || staffUser.role === 'Admin'
        ? 'police'
        : 'counselor'
      : 'citizen'
    const authenticatedUser: AuthUser = {
      name: staffUser?.name ?? email.split('@')[0] ?? 'Citizen',
      email,
      role,
    }

    set({ user: authenticatedUser, isAuthenticated: true })
    return authenticatedUser
  },

  logout: () => set({ user: null, isAuthenticated: false }),
}))

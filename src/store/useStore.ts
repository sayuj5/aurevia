import { create } from 'zustand'
import type { CaseRecord } from '../data/mockCases'
import type { NotificationItem } from '../data/mockUsers'

type AuthRole = 'counselor' | 'police' | 'citizen' | null

interface AuthUser {
  email: string
  role: AuthRole
}

interface CaseSlice {
  cases: CaseRecord[]
  setCases: (cases: CaseRecord[]) => void
  updateCaseRisk: (caseId: string, newScore: number, tier?: CaseRecord['tier']) => void
  updateCaseStatus: (caseId: string, status: CaseRecord['status']) => void
  updateCaseAssignee: (caseId: string, assignedTo: string) => void
}

interface NotificationSlice {
  notifications: NotificationItem[]
  setNotifications: (notifications: NotificationItem[]) => void
  addLiveNotification: (notification: NotificationItem) => void
  markAllNotificationsRead: () => void
}

interface AuthSessionSlice {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, role: string) => void
  logout: () => void
}

const normalizeRole = (role: string): Exclude<AuthRole, null> | null => {
  if (role === 'counselor' || role === 'police' || role === 'citizen') return role
  return null
}

export type AppStoreState = CaseSlice & NotificationSlice & AuthSessionSlice

export const useStore = create<AppStoreState>((set) => ({
  cases: [],
  notifications: [],
  user: null,
  isAuthenticated: false,

  setCases: (cases) => set({ cases }),

  updateCaseRisk: (caseId, newScore, tier) =>
    set((state) => ({
      cases: state.cases.map((c) =>
        c.id === caseId ? { ...c, score: newScore, tier: tier ?? c.tier, lastUpdate: 'just now' } : c
      ),
    })),

  updateCaseStatus: (caseId, status) =>
    set((state) => ({
      cases: state.cases.map((c) => (c.id === caseId ? { ...c, status } : c)),
    })),

  updateCaseAssignee: (caseId, assignedTo) =>
    set((state) => ({
      cases: state.cases.map((c) => (c.id === caseId ? { ...c, assignedTo: assignedTo || null } : c)),
    })),

  setNotifications: (notifications) => set({ notifications }),

  addLiveNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
    })),

  markAllNotificationsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    })),

  login: (email, role) =>
    set({
      user: { email, role: normalizeRole(role) },
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      isAuthenticated: false,
    }),
}))

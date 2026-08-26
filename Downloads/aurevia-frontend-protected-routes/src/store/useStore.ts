import { create } from 'zustand'
import type { CaseRecord, Tier } from '../data/mockCases'
import type { NotificationItem } from '../data/mockUsers'

interface AppState {
  // --- Cases (single source of truth for Dashboard + Case Management) ---
  cases: CaseRecord[]
  setCases: (cases: CaseRecord[]) => void
  updateCaseRisk: (caseId: string, newScore: number, tier?: Tier) => void
  updateCaseStatus: (caseId: string, status: CaseRecord['status']) => void
  updateCaseAssignee: (caseId: string, assignedTo: string) => void

  // --- Notifications ---
  notifications: NotificationItem[]
  setNotifications: (notifications: NotificationItem[]) => void
  addLiveNotification: (notification: NotificationItem) => void
  markAllNotificationsRead: () => void
}

export const useStore = create<AppState>((set) => ({
  cases: [],
  notifications: [],

  setCases: (cases) => set({ cases }),

  updateCaseRisk: (caseId, newScore, tier) =>
    set((state) => ({
      cases: state.cases.map((c) =>
        c.id === caseId
          ? { ...c, score: newScore, tier: tier ?? c.tier, lastUpdate: 'just now' }
          : c
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
}))

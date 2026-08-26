export interface AppUser {
  id: string
  name: string
  email: string
  role: 'Counsellor' | 'Officer' | 'Admin'
  district: string
  status: 'active' | 'suspended'
  caseload: number
}

export const mockUsers: AppUser[] = [
  { id: 'u1', name: 'S. Kulkarni', email: 's.kulkarni@aurevia.org', role: 'Counsellor', district: 'Pune, MH', status: 'active', caseload: 12 },
  { id: 'u2', name: 'R. Deshmukh', email: 'r.deshmukh@aurevia.org', role: 'Officer', district: 'Latur, MH', status: 'active', caseload: 8 },
  { id: 'u3', name: 'A. Verma', email: 'a.verma@aurevia.org', role: 'Counsellor', district: 'Nagpur, MH', status: 'active', caseload: 15 },
  { id: 'u4', name: 'P. Joshi', email: 'p.joshi@aurevia.org', role: 'Admin', district: 'HQ', status: 'active', caseload: 0 },
  { id: 'u5', name: 'N. Shaikh', email: 'n.shaikh@aurevia.org', role: 'Officer', district: 'Aurangabad, MH', status: 'suspended', caseload: 0 },
]

export interface NotificationItem {
  id: string
  caseCode: string
  tier: 'low' | 'moderate' | 'high' | 'critical'
  message: string
  timestamp: string
  channel: 'websocket' | 'telegram' | 'fcm' | 'email'
  read: boolean
}

export const mockNotifications: NotificationItem[] = [
  { id: 'n1', caseCode: 'AV-2291', tier: 'critical', message: 'Risk score crossed 85 — immediate protection alert triggered.', timestamp: '4 min ago', channel: 'telegram', read: false },
  { id: 'n2', caseCode: 'AV-2299', tier: 'high', message: 'New incident report filed, awaiting counsellor review.', timestamp: '9 min ago', channel: 'websocket', read: false },
  { id: 'n3', caseCode: 'AV-2287', tier: 'high', message: 'Repeated intimidation reference flagged in latest text check-in.', timestamp: '22 min ago', channel: 'fcm', read: false },
  { id: 'n4', caseCode: 'AV-2264', tier: 'moderate', message: 'Weekly routine check-in reminder sent to counsellor.', timestamp: '1 hr ago', channel: 'email', read: true },
  { id: 'n5', caseCode: 'AV-2231', tier: 'low', message: 'Case marked closed after three stable assessments.', timestamp: '3 hr ago', channel: 'email', read: true },
]

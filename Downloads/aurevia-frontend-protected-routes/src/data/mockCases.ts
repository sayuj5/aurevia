export type Tier = 'low' | 'moderate' | 'high' | 'critical'

export interface CaseRecord {
  id: string
  code: string // anonymized reference code, never a real name
  score: number // 0-100
  tier: Tier
  trend: 'rising' | 'falling' | 'flat'
  lastUpdate: string
  district: string
  signals: { nlp: number; vocal: number; caseHistory: number }
  summary: string
  language: string
  awaitingReview: boolean
  status: 'open' | 'in_review' | 'closed'
  assignedTo: string | null
  lat: number
  lng: number
  featureAttribution: { feature: string; contribution: number }[]
}

export const tierMeta: Record<Tier, { label: string; color: string; range: string }> = {
  low: { label: 'Low', color: 'var(--color-sage-light)', range: '0–39' },
  moderate: { label: 'Moderate', color: '#D9A441', range: '40–64' },
  high: { label: 'High', color: 'var(--color-terracotta)', range: '65–84' },
  critical: { label: 'Critical', color: 'var(--color-brick)', range: '85–100' },
}

export const mockCases: CaseRecord[] = [
  {
    id: 'c1',
    code: 'AV-2291',
    score: 91,
    tier: 'critical',
    trend: 'rising',
    lastUpdate: '4 min ago',
    district: 'Nashik, MH',
    signals: { nlp: 0.88, vocal: 0.93, caseHistory: 0.7 },
    summary: 'Voice biomarkers show sharp acute stress spike during follow-up. Court hearing in 2 days.',
    language: 'Marathi',
    awaitingReview: true,
    status: 'open',
    assignedTo: null,
    lat: 19.9975,
    lng: 73.7898,
    featureAttribution: [
      { feature: 'Vocal pitch instability', contribution: 0.34 },
      { feature: 'Speaking pause ratio', contribution: 0.26 },
      { feature: 'Upcoming court hearing (2 days)', contribution: 0.21 },
      { feature: 'Text distress keywords', contribution: 0.19 },
    ],
  },
  {
    id: 'c2',
    code: 'AV-2287',
    score: 78,
    tier: 'high',
    trend: 'rising',
    lastUpdate: '22 min ago',
    district: 'Latur, MH',
    signals: { nlp: 0.81, vocal: 0.6, caseHistory: 0.55 },
    summary: 'Text assessment flags repeated references to intimidation from named individual.',
    language: 'Hindi',
    awaitingReview: true,
    status: 'open',
    assignedTo: 'R. Deshmukh',
    lat: 18.4088,
    lng: 76.5604,
    featureAttribution: [
      { feature: 'Repeated intimidation references', contribution: 0.4 },
      { feature: 'Text sentiment (NLP)', contribution: 0.31 },
      { feature: 'Case history escalation', contribution: 0.18 },
      { feature: 'Vocal biomarker', contribution: 0.11 },
    ],
  },
  {
    id: 'c3',
    code: 'AV-2264',
    score: 52,
    tier: 'moderate',
    trend: 'flat',
    lastUpdate: '1 hr ago',
    district: 'Pune, MH',
    signals: { nlp: 0.5, vocal: 0.48, caseHistory: 0.4 },
    summary: 'Stable since last assessment. Routine check-in recommended within the week.',
    language: 'Marathi',
    awaitingReview: false,
    status: 'in_review',
    assignedTo: 'S. Kulkarni',
    lat: 18.5204,
    lng: 73.8567,
    featureAttribution: [
      { feature: 'Text sentiment (NLP)', contribution: 0.3 },
      { feature: 'Vocal biomarker', contribution: 0.29 },
      { feature: 'Case history', contribution: 0.24 },
      { feature: 'Follow-up consistency', contribution: 0.17 },
    ],
  },
  {
    id: 'c4',
    code: 'AV-2231',
    score: 34,
    tier: 'low',
    trend: 'falling',
    lastUpdate: '3 hr ago',
    district: 'Nagpur, MH',
    signals: { nlp: 0.3, vocal: 0.28, caseHistory: 0.2 },
    summary: 'Improvement over last three assessments. Support plan appears effective.',
    language: 'English',
    awaitingReview: false,
    status: 'closed',
    assignedTo: 'A. Verma',
    lat: 21.1458,
    lng: 79.0882,
    featureAttribution: [
      { feature: 'Declining vocal distress', contribution: 0.35 },
      { feature: 'Text sentiment (NLP)', contribution: 0.28 },
      { feature: 'Case history', contribution: 0.22 },
      { feature: 'Support plan adherence', contribution: 0.15 },
    ],
  },
  {
    id: 'c5',
    code: 'AV-2299',
    score: 68,
    tier: 'high',
    trend: 'rising',
    lastUpdate: '9 min ago',
    district: 'Aurangabad, MH',
    signals: { nlp: 0.6, vocal: 0.7, caseHistory: 0.65 },
    summary: 'New incident report filed. Acoustic pause ratio elevated versus baseline.',
    language: 'Hindi',
    awaitingReview: true,
    status: 'open',
    assignedTo: null,
    lat: 19.8762,
    lng: 75.3433,
    featureAttribution: [
      { feature: 'Acoustic pause ratio', contribution: 0.33 },
      { feature: 'New incident filed', contribution: 0.3 },
      { feature: 'Vocal biomarker', contribution: 0.22 },
      { feature: 'Text sentiment (NLP)', contribution: 0.15 },
    ],
  },
]

import { mockCases, tierMeta, type CaseRecord, type Tier } from '../data/mockCases'

export type { CaseRecord, Tier }
export { tierMeta }

export function fetchCases(): Promise<CaseRecord[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockCases), 500)
  })
}

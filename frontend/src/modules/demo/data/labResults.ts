// Stub for lab results - real fixtures land in P6 (US2). Returns empty
// arrays for now so the demo module type-checks; lab-results screen will
// show its empty state until P6 fills the data.

import type { LabResult, BiomarkerReference } from '@/types'
import { getOrCreate } from '../cache'

export function getDemoBiomarkers(): BiomarkerReference[] {
  return getOrCreate<BiomarkerReference[]>('biomarkers', () => [])
}

export function getDemoLabResults(): LabResult[] {
  return getOrCreate<LabResult[]>('labResults', () => [])
}

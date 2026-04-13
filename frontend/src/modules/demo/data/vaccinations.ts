// Stub for vaccinations - real fixtures land in P6 (US2).

import type { Vaccination } from '@/types'
import { getOrCreate } from '../cache'

export function getDemoVaccinations(): Vaccination[] {
  return getOrCreate<Vaccination[]>('vaccinations', () => [])
}

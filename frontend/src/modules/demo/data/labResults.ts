// Demo lab results: >=4 results, each with >=3 biomarker entries.
// Includes a mix of in-range and out-of-range values so the UI's
// normal/abnormal badges have something to render (US2.4).

import type { LabResult, BiomarkerReference, LabTestEntry } from '@/types'
import { getOrCreate } from '../cache'
import { mulberry32, dailySeed, floatBetween } from '../seed'
import { getDemoVisits } from './visits'

interface BiomarkerSeed {
  name: string
  abbreviation: string | null
  unit: string
  category: string
  ref_min: number
  ref_max: number
}

const BIOMARKERS: BiomarkerSeed[] = [
  { name: 'Гемоглобін', abbreviation: 'Hb', unit: 'г/л', category: 'Загальний аналіз крові', ref_min: 130, ref_max: 170 },
  { name: 'Лейкоцити', abbreviation: 'WBC', unit: '10^9/л', category: 'Загальний аналіз крові', ref_min: 4, ref_max: 9 },
  { name: 'Тромбоцити', abbreviation: 'PLT', unit: '10^9/л', category: 'Загальний аналіз крові', ref_min: 150, ref_max: 400 },
  { name: 'Глюкоза', abbreviation: 'GLU', unit: 'ммоль/л', category: 'Біохімія', ref_min: 3.9, ref_max: 6.1 },
  { name: 'Холестерин', abbreviation: 'CHOL', unit: 'ммоль/л', category: 'Біохімія', ref_min: 0, ref_max: 5.2 },
  { name: 'Креатинін', abbreviation: 'CREA', unit: 'мкмоль/л', category: 'Біохімія', ref_min: 60, ref_max: 110 },
  { name: 'АЛТ', abbreviation: 'ALT', unit: 'Од/л', category: 'Печінкові проби', ref_min: 7, ref_max: 55 },
  { name: 'ТТГ', abbreviation: 'TSH', unit: 'мМО/л', category: 'Гормони', ref_min: 0.4, ref_max: 4.0 },
]

export function getDemoBiomarkers(): BiomarkerReference[] {
  return getOrCreate<BiomarkerReference[]>('biomarkers', () => {
    const now = new Date().toISOString()
    return BIOMARKERS.map((b, idx) => ({
      id: idx + 1,
      name: b.name,
      abbreviation: b.abbreviation,
      unit: b.unit,
      category: b.category,
      ref_min: b.ref_min,
      ref_max: b.ref_max,
      ref_min_male: b.ref_min,
      ref_max_male: b.ref_max,
      ref_min_female: b.ref_min,
      ref_max_female: b.ref_max,
      sort_order: idx,
      created: now,
      updated: now,
    }))
  })
}

export function getDemoLabResults(): LabResult[] {
  return getOrCreate<LabResult[]>('labResults', () => {
    const rng = mulberry32(dailySeed() ^ 0xab)
    const biomarkers = getDemoBiomarkers()
    const visits = getDemoVisits()
    const results: LabResult[] = []
    const today = new Date()

    for (let i = 0; i < 5; i++) {
      const daysAgo = i * 30 + Math.floor(rng() * 10)
      const date = new Date(today.getTime() - daysAgo * 86_400_000).toISOString().slice(0, 10)
      const entries: LabTestEntry[] = []
      // Pick 4 distinct biomarkers per result
      const indexes = [0, 1, 2, 3].map((j) => (i + j) % biomarkers.length)
      indexes.forEach((bIdx, jdx) => {
        const b = biomarkers[bIdx]!
        // Force at least one out-of-range value per result for badge demo
        const outOfRange = jdx === 0 && i % 2 === 0
        const value = outOfRange
          ? floatBetween(rng, (b.ref_max ?? 0) * 1.05, (b.ref_max ?? 0) * 1.4, 1)
          : floatBetween(rng, b.ref_min ?? 0, b.ref_max ?? 1, 1)
        entries.push({
          id: results.length * 10 + jdx,
          biomarker_id: b.id,
          biomarker_name: b.name,
          value,
          unit: b.unit,
          ref_min: b.ref_min,
          ref_max: b.ref_max,
          is_normal: value >= (b.ref_min ?? -Infinity) && value <= (b.ref_max ?? Infinity),
        })
      })
      const visit = visits[i % visits.length]
      const createdIso = `${date}T09:00:00.000Z`
      results.push({
        id: i + 1,
        visit_id: visit?.id ?? null,
        date,
        notes: i % 2 === 0 ? 'Планова перевірка.' : null,
        entries,
        entries_count: entries.length,
        out_of_range_count: entries.filter((e) => e.is_normal === false).length,
        visit_date: visit?.date,
        visit_procedure: visit?.procedure?.name,
        created: createdIso,
        updated: createdIso,
      })
    }
    return results.sort((a, b) => b.date.localeCompare(a.date))
  })
}

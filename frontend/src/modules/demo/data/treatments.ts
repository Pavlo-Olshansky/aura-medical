// Demo Treatment fixtures: >=6 treatments mixing active and completed
// status (computed from date_start + days vs today, FR-012).

import type { Treatment } from '@/types'
import { getOrCreate } from '../cache'

interface SeedTreatment {
  name: string
  days: number
  daysAgo: number // negative = future start
  receipt: string
  body_region: string | null
}

const SEEDS: SeedTreatment[] = [
  { name: 'Парацетамол 500мг', days: 5, daysAgo: 60, receipt: '1 таблетка тричі на день', body_region: 'head' },
  { name: 'Амоксицилін', days: 7, daysAgo: 45, receipt: '500мг кожні 8 годин', body_region: 'chest' },
  { name: 'Вітамін D3', days: 30, daysAgo: 5, receipt: '2000 МО на день', body_region: null },
  { name: 'Омепразол', days: 14, daysAgo: 3, receipt: '20мг вранці натщесерце', body_region: 'abdomen' },
  { name: 'Лізиноприл', days: 90, daysAgo: 1, receipt: '10мг на день', body_region: 'chest' },
  { name: 'Ібупрофен', days: 3, daysAgo: 30, receipt: '400мг при болю', body_region: 'limbs' },
]

export function getDemoTreatments(): Treatment[] {
  return getOrCreate<Treatment[]>('treatments', () => {
    const today = new Date()
    return SEEDS.map((seed, idx) => {
      const start = new Date(today.getTime() - seed.daysAgo * 86_400_000)
      const startIso = start.toISOString().slice(0, 10)
      const end = new Date(start.getTime() + seed.days * 86_400_000)
      const status: Treatment['status'] = end < today ? 'completed' : 'active'
      const createdIso = new Date(start.getTime() - 3600_000).toISOString()
      return {
        id: idx + 1,
        date_start: startIso,
        name: seed.name,
        days: seed.days,
        receipt: seed.receipt,
        status,
        body_region: seed.body_region,
        created: createdIso,
        updated: createdIso,
      }
    })
  })
}

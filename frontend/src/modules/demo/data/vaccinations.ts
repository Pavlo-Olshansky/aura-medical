// Demo vaccinations: >=3 entries covering all 3 statuses
// (upcoming, overdue, completed).

import type { Vaccination } from '@/types'
import { getOrCreate } from '../cache'

interface VaccinationSeed {
  vaccine_name: string
  manufacturer: string
  daysAgo: number
  next_due_offset_days: number | null
  status: Vaccination['status']
  dose_number: number
  notes: string | null
}

const SEEDS: VaccinationSeed[] = [
  {
    vaccine_name: 'COVID-19 (Pfizer)',
    manufacturer: 'Pfizer-BioNTech',
    daysAgo: 180,
    next_due_offset_days: null,
    status: 'completed',
    dose_number: 3,
    notes: 'Бустерна доза.',
  },
  {
    vaccine_name: 'Грип (Vaxigrip Tetra)',
    manufacturer: 'Sanofi Pasteur',
    daysAgo: 400,
    next_due_offset_days: -180,
    status: 'overdue',
    dose_number: 5,
    notes: 'Щорічна вакцинація.',
  },
  {
    vaccine_name: 'Кір-Краснуха-Паротит (КПК)',
    manufacturer: 'GSK',
    daysAgo: 365 * 10,
    next_due_offset_days: 30,
    status: 'upcoming',
    dose_number: 2,
    notes: null,
  },
]

export function getDemoVaccinations(): Vaccination[] {
  return getOrCreate<Vaccination[]>('vaccinations', () => {
    const today = new Date()
    return SEEDS.map((seed, idx) => {
      const date = new Date(today.getTime() - seed.daysAgo * 86_400_000)
        .toISOString()
        .slice(0, 10)
      const next = seed.next_due_offset_days != null
        ? new Date(today.getTime() + seed.next_due_offset_days * 86_400_000).toISOString().slice(0, 10)
        : null
      const createdIso = `${date}T10:00:00.000Z`
      return {
        id: idx + 1,
        date,
        vaccine_name: seed.vaccine_name,
        manufacturer: seed.manufacturer,
        lot_number: `LOT-${1000 + idx}`,
        dose_number: seed.dose_number,
        next_due_date: next,
        notes: seed.notes,
        has_document: false,
        status: seed.status,
        created: createdIso,
        updated: createdIso,
      }
    })
  })
}

// Demo Visit fixtures: >=12 visits over the past 18 months (FR-012).
// `document` and `link` are always null per FR-017 / Q1 so DocumentPreview
// renders gracefully without 404s.

import type { Visit } from '@/types'
import { getOrCreate } from '../cache'
import { mulberry32, dailySeed, pick, intBetween } from '../seed'
import { getDemoReferences } from './references'

const DOCTORS = [
  'Іванов І.І.',
  'Петренко О.В.',
  'Коваленко М.С.',
  'Шевчук Н.П.',
  'Бондаренко В.І.',
  'Мельник Т.О.',
]

const BODY_REGIONS = ['head', 'chest', 'abdomen', 'back', 'limbs', 'neck']

const COMMENTS = [
  'Загальний стан задовільний.',
  'Рекомендовано повторний візит через місяць.',
  'Без особливостей.',
  'Призначено лікування.',
  'Аналізи в межах норми.',
  'Подальше спостереження.',
]

export function getDemoVisits(): Visit[] {
  return getOrCreate<Visit[]>('visits', () => {
    const rng = mulberry32(dailySeed())
    const positions = getDemoReferences('positions')
    const procedures = getDemoReferences('procedures')
    const clinics = getDemoReferences('clinics')
    const cities = getDemoReferences('cities')

    const visits: Visit[] = []
    const today = new Date()
    // Spread 14 visits across the past 18 months
    for (let i = 0; i < 14; i++) {
      const daysAgo = Math.floor(((i + 1) * 540) / 14) + intBetween(rng, -10, 10)
      const date = new Date(today.getTime() - daysAgo * 86_400_000)
      const dateIso = date.toISOString().slice(0, 10)
      const createdIso = new Date(date.getTime() - 86_400_000).toISOString()
      visits.push({
        id: i + 1,
        date: dateIso,
        position: pick(rng, positions),
        doctor: pick(rng, DOCTORS),
        procedure: pick(rng, procedures),
        procedure_details: rng() > 0.5 ? pick(rng, COMMENTS) : null,
        clinic: pick(rng, clinics),
        city: pick(rng, cities),
        document: null,
        has_document: false,
        body_region: pick(rng, BODY_REGIONS),
        link: null,
        comment: rng() > 0.4 ? pick(rng, COMMENTS) : null,
        price: intBetween(rng, 200, 3000),
        created: createdIso,
        updated: createdIso,
      })
    }
    // Newest first to match typical API ordering
    return visits.sort((a, b) => b.date.localeCompare(a.date))
  })
}

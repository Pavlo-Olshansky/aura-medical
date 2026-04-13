// Reference data fixtures: positions, procedures, clinics, cities (FR-012).
// Five+ realistic Ukrainian entries per kind. Stable across the lifetime of
// a page load via the cache.

import type { Reference } from '@/types'
import { getOrCreate } from '../cache'

type RefKind = 'positions' | 'procedures' | 'clinics' | 'cities'

const POSITIONS = ['Терапевт', 'Кардіолог', 'Невролог', 'Стоматолог', 'Офтальмолог', 'Ендокринолог']
const PROCEDURES = [
  'Консультація',
  'УЗД',
  'ЕКГ',
  'Загальний аналіз крові',
  'МРТ',
  'Профілактичний огляд',
]
const CLINICS = [
  'Медібор',
  'Добробут',
  'Обласна лікарня',
  'Центр сімейної медицини',
  'Поліклініка №3',
  'Інвітро',
]
const CITIES = ['Київ', 'Львів', 'Одеса', 'Харків', 'Дніпро']

function buildRefs(names: readonly string[]): Reference[] {
  const now = new Date().toISOString()
  return names.map((name, idx) => ({
    id: idx + 1,
    name,
    created: now,
    updated: now,
  }))
}

export function getDemoReferences(kind: RefKind): Reference[] {
  return getOrCreate(`refs:${kind}`, () => {
    switch (kind) {
      case 'positions':
        return buildRefs(POSITIONS)
      case 'procedures':
        return buildRefs(PROCEDURES)
      case 'clinics':
        return buildRefs(CLINICS)
      case 'cities':
        return buildRefs(CITIES)
    }
  })
}

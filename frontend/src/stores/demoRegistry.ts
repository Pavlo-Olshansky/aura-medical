// Lightweight registry of demo data accessors. Populated by the lazy demo
// module on activation, consumed synchronously by every Pinia store. This
// indirection lets stores call demo accessors without statically importing
// the lazy `@/modules/demo` chunk (research.md R3).

import type {
  Reference,
  Visit,
  Treatment,
  LabResult,
  BiomarkerReference,
  HealthMetric,
  MetricType,
  Vaccination,
  CalendarEvent,
  ProfileData,
  User,
} from '@/types'
import type { Reminder } from '@/api/notifications'
import type { WeatherSummary, WeatherDetail } from '@/types/weather'

export interface DemoAccessors {
  getUser: () => User
  getProfile: () => ProfileData
  getReferences: (kind: 'positions' | 'procedures' | 'clinics' | 'cities') => Reference[]
  getVisits: () => Visit[]
  getTreatments: () => Treatment[]
  getLabResults: () => LabResult[]
  getBiomarkers: () => BiomarkerReference[]
  getMetricTypes: () => MetricType[]
  getHealthMetrics: () => HealthMetric[]
  getVaccinations: () => Vaccination[]
  getCalendarEvents: (from: string, to: string) => CalendarEvent[]
  getNotifications: () => Reminder[]
  getWeatherSummary: () => WeatherSummary
  getWeatherDetail: () => WeatherDetail
  create: <T extends { id: number }>(collection: T[], record: Omit<T, 'id'>) => T
  update: <T extends { id: number }>(collection: T[], id: number, patch: Partial<T>) => T | undefined
  remove: <T extends { id: number }>(collection: T[], id: number) => boolean
}

let registry: DemoAccessors | null = null

export function registerDemoAccessors(accessors: DemoAccessors): void {
  registry = accessors
}

export function unregisterDemoAccessors(): void {
  registry = null
}

export function demo(): DemoAccessors {
  if (!registry) {
    throw new Error('Demo accessors are not registered. activateDemo() must be called first.')
  }
  return registry
}

// Sort an array of records by a string-keyed field. Used by every list
// store's demo branch to honor sort_by/sort_order from filter params.
export function demoSort<T>(items: T[], sortBy: string, sortOrder: 'asc' | 'desc' = 'desc'): T[] {
  const dir = sortOrder === 'asc' ? 1 : -1
  return [...items].sort((a, b) => {
    const av = (a as unknown as Record<string, unknown>)[sortBy] ?? ''
    const bv = (b as unknown as Record<string, unknown>)[sortBy] ?? ''
    return String(av).localeCompare(String(bv)) * dir
  })
}

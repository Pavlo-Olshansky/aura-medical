// Demo health metrics: 3 metric types, >=10 datapoints each over 90 days.
// Includes blood pressure (with secondary value), weight, heart rate.

import type { HealthMetric, MetricType } from '@/types'
import { getOrCreate } from '../cache'
import { mulberry32, dailySeed, floatBetween } from '../seed'

interface MetricSeed {
  name: string
  unit: string
  has_secondary_value: boolean
  ref_min: number | null
  ref_max: number | null
  ref_min_secondary: number | null
  ref_max_secondary: number | null
  cadenceDays: number
  rangePrimary: [number, number]
  rangeSecondary?: [number, number]
}

const METRICS: MetricSeed[] = [
  {
    name: 'Артеріальний тиск',
    unit: 'мм рт.ст.',
    has_secondary_value: true,
    ref_min: 110,
    ref_max: 130,
    ref_min_secondary: 70,
    ref_max_secondary: 85,
    cadenceDays: 3,
    rangePrimary: [108, 138],
    rangeSecondary: [68, 88],
  },
  {
    name: 'Вага',
    unit: 'кг',
    has_secondary_value: false,
    ref_min: 70,
    ref_max: 80,
    ref_min_secondary: null,
    ref_max_secondary: null,
    cadenceDays: 7,
    rangePrimary: [73, 77],
  },
  {
    name: 'Пульс',
    unit: 'уд/хв',
    has_secondary_value: false,
    ref_min: 60,
    ref_max: 80,
    ref_min_secondary: null,
    ref_max_secondary: null,
    cadenceDays: 3,
    rangePrimary: [60, 82],
  },
]

export function getDemoMetricTypes(): MetricType[] {
  return getOrCreate<MetricType[]>('metricTypes', () => {
    const now = new Date().toISOString()
    return METRICS.map((m, idx) => ({
      id: idx + 1,
      name: m.name,
      unit: m.unit,
      has_secondary_value: m.has_secondary_value,
      ref_min: m.ref_min,
      ref_max: m.ref_max,
      ref_min_secondary: m.ref_min_secondary,
      ref_max_secondary: m.ref_max_secondary,
      sort_order: idx,
      created: now,
      updated: now,
    }))
  })
}

export function getDemoHealthMetrics(): HealthMetric[] {
  return getOrCreate<HealthMetric[]>('healthMetrics', () => {
    const rng = mulberry32(dailySeed() ^ 0xcd)
    const types = getDemoMetricTypes()
    const points: HealthMetric[] = []
    const today = new Date()
    let nextId = 1

    METRICS.forEach((seed, typeIdx) => {
      const type = types[typeIdx]!
      for (let day = 90; day >= 0; day -= seed.cadenceDays) {
        const date = new Date(today.getTime() - day * 86_400_000).toISOString().slice(0, 10)
        const value = floatBetween(rng, seed.rangePrimary[0], seed.rangePrimary[1], 1)
        const secondary = seed.rangeSecondary
          ? floatBetween(rng, seed.rangeSecondary[0], seed.rangeSecondary[1], 0)
          : null
        points.push({
          id: nextId++,
          metric_type_id: type.id,
          metric_type: type,
          date,
          value,
          secondary_value: secondary,
          notes: null,
          created: `${date}T08:00:00.000Z`,
          updated: `${date}T08:00:00.000Z`,
        })
      }
    })
    return points.sort((a, b) => b.date.localeCompare(a.date))
  })
}

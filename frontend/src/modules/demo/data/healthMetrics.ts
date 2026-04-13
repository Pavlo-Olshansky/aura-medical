// Stub for health metrics - real fixtures land in P6 (US2).

import type { HealthMetric, MetricType } from '@/types'
import { getOrCreate } from '../cache'

export function getDemoMetricTypes(): MetricType[] {
  return getOrCreate<MetricType[]>('metricTypes', () => [])
}

export function getDemoHealthMetrics(): HealthMetric[] {
  return getOrCreate<HealthMetric[]>('healthMetrics', () => [])
}

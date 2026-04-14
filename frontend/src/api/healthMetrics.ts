import { apiClient } from '@/api/client'
import type { HealthMetric, MetricType, PaginatedResponse } from '@/types'
import type { HealthMetricPayload, MetricTypePayload } from '@/types/payloads'

export interface HealthMetricListParams {
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  metric_type_id?: number
  date_from?: string
  date_to?: string
}

export interface MetricTrendParams {
  metric_type_id: number
  date_from?: string
  date_to?: string
}

export interface MetricTrendPoint {
  date: string
  value: number
  secondary_value: number | null
}

export async function listHealthMetrics(params?: HealthMetricListParams): Promise<PaginatedResponse<HealthMetric>> {
  const response = await apiClient.get('/api/v1/health-metrics/', { params })
  return response.data
}

export async function getHealthMetric(id: number): Promise<HealthMetric> {
  const response = await apiClient.get(`/api/v1/health-metrics/${id}`)
  return response.data
}

export async function createHealthMetric(data: HealthMetricPayload): Promise<HealthMetric> {
  const response = await apiClient.post('/api/v1/health-metrics/', data)
  return response.data
}

export async function updateHealthMetric(id: number, data: Partial<HealthMetricPayload>): Promise<HealthMetric> {
  const response = await apiClient.put(`/api/v1/health-metrics/${id}`, data)
  return response.data
}

export async function deleteHealthMetric(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/health-metrics/${id}`)
}

export interface MetricTrendResponse {
  metric_type: string
  unit: string
  ref_min: number | null
  ref_max: number | null
  ref_min_secondary: number | null
  ref_max_secondary: number | null
  data_points: MetricTrendPoint[]
}

export async function getMetricTrend(params: MetricTrendParams): Promise<MetricTrendPoint[]> {
  const response = await apiClient.get<MetricTrendResponse>('/api/v1/health-metrics/trend', { params })
  return response.data.data_points
}

// Metric types
export async function listMetricTypes(search?: string): Promise<MetricType[]> {
  const response = await apiClient.get('/api/v1/metric-types/', {
    params: search ? { search } : {},
  })
  return response.data
}

export async function createMetricType(data: MetricTypePayload): Promise<MetricType> {
  const response = await apiClient.post('/api/v1/metric-types/', data)
  return response.data
}

export async function updateMetricType(id: number, data: Partial<MetricTypePayload>): Promise<MetricType> {
  const response = await apiClient.put(`/api/v1/metric-types/${id}`, data)
  return response.data
}

export async function deleteMetricType(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/metric-types/${id}`)
}

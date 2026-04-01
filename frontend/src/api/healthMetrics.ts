import { apiClient } from '@/api/client'
import type { HealthMetric, MetricType, PaginatedResponse } from '@/types'

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
  const response = await apiClient.get('/api/health-metrics/', { params })
  return response.data
}

export async function getHealthMetric(id: number): Promise<HealthMetric> {
  const response = await apiClient.get(`/api/health-metrics/${id}`)
  return response.data
}

export async function createHealthMetric(data: any): Promise<HealthMetric> {
  const response = await apiClient.post('/api/health-metrics/', data)
  return response.data
}

export async function updateHealthMetric(id: number, data: any): Promise<HealthMetric> {
  const response = await apiClient.put(`/api/health-metrics/${id}`, data)
  return response.data
}

export async function deleteHealthMetric(id: number): Promise<void> {
  await apiClient.delete(`/api/health-metrics/${id}`)
}

export async function getMetricTrend(params: MetricTrendParams): Promise<MetricTrendPoint[]> {
  const response = await apiClient.get('/api/health-metrics/trend', { params })
  return response.data
}

// Metric types
export async function listMetricTypes(search?: string): Promise<MetricType[]> {
  const response = await apiClient.get('/api/metric-types/', {
    params: search ? { search } : {},
  })
  return response.data
}

export async function createMetricType(data: any): Promise<MetricType> {
  const response = await apiClient.post('/api/metric-types/', data)
  return response.data
}

export async function updateMetricType(id: number, data: any): Promise<MetricType> {
  const response = await apiClient.put(`/api/metric-types/${id}`, data)
  return response.data
}

export async function deleteMetricType(id: number): Promise<void> {
  await apiClient.delete(`/api/metric-types/${id}`)
}

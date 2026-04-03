import { apiClient } from '@/api/client'
import type { Treatment, PaginatedResponse } from '@/types'

export interface TreatmentListParams {
  page?: number
  size?: number
  status?: 'active' | 'completed'
}

export interface TreatmentPayload {
  name: string
  date_start: string
  days: number
  receipt: string
  body_region?: string | null
}

export async function listTreatments(params?: TreatmentListParams): Promise<PaginatedResponse<Treatment>> {
  const response = await apiClient.get('/api/v1/treatments/', { params })
  return response.data
}

export async function getTreatment(id: number): Promise<Treatment> {
  const response = await apiClient.get(`/api/v1/treatments/${id}`)
  return response.data
}

export async function createTreatment(data: TreatmentPayload): Promise<Treatment> {
  const response = await apiClient.post('/api/v1/treatments/', data)
  return response.data
}

export async function updateTreatment(id: number, data: TreatmentPayload): Promise<Treatment> {
  const response = await apiClient.put(`/api/v1/treatments/${id}`, data)
  return response.data
}

export async function deleteTreatment(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/treatments/${id}`)
}

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
}

export async function listTreatments(params?: TreatmentListParams): Promise<PaginatedResponse<Treatment>> {
  const response = await apiClient.get('/api/treatments/', { params })
  return response.data
}

export async function getTreatment(id: number): Promise<Treatment> {
  const response = await apiClient.get(`/api/treatments/${id}`)
  return response.data
}

export async function createTreatment(data: TreatmentPayload): Promise<Treatment> {
  const response = await apiClient.post('/api/treatments/', data)
  return response.data
}

export async function updateTreatment(id: number, data: TreatmentPayload): Promise<Treatment> {
  const response = await apiClient.put(`/api/treatments/${id}`, data)
  return response.data
}

export async function deleteTreatment(id: number): Promise<void> {
  await apiClient.delete(`/api/treatments/${id}`)
}

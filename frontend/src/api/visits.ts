import { apiClient } from '@/api/client'
import type { Visit, PaginatedResponse } from '@/types'

export interface VisitListParams {
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  date_from?: string
  date_to?: string
  clinic_id?: number
  city_id?: number
  procedure_id?: number
  position_id?: number
}

export async function listVisits(params?: VisitListParams): Promise<PaginatedResponse<Visit>> {
  const response = await apiClient.get('/api/v1/visits/', { params })
  return response.data
}

export async function getVisit(id: number): Promise<Visit> {
  const response = await apiClient.get(`/api/v1/visits/${id}`)
  return response.data
}

export async function createVisit(formData: FormData): Promise<Visit> {
  const response = await apiClient.post('/api/v1/visits/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function updateVisit(id: number, formData: FormData): Promise<Visit> {
  const response = await apiClient.put(`/api/v1/visits/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function deleteVisit(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/visits/${id}`)
}

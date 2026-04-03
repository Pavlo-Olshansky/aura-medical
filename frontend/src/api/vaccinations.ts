import { apiClient } from '@/api/client'
import type { Vaccination, PaginatedResponse } from '@/types'

export interface VaccinationListParams {
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  status?: 'upcoming' | 'overdue' | 'completed'
  date_from?: string
  date_to?: string
}

export async function listVaccinations(params?: VaccinationListParams): Promise<PaginatedResponse<Vaccination>> {
  const response = await apiClient.get('/api/v1/vaccinations/', { params })
  return response.data
}

export async function getVaccination(id: number): Promise<Vaccination> {
  const response = await apiClient.get(`/api/v1/vaccinations/${id}`)
  return response.data
}

export async function createVaccination(formData: FormData): Promise<Vaccination> {
  const response = await apiClient.post('/api/v1/vaccinations/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function updateVaccination(id: number, formData: FormData): Promise<Vaccination> {
  const response = await apiClient.put(`/api/v1/vaccinations/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function deleteVaccination(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/vaccinations/${id}`)
}

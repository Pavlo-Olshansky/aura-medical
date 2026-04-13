import { apiClient } from '@/api/client'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import type { LabResult, BiomarkerReference, PaginatedResponse } from '@/types'
import type { LabResultPayload, BiomarkerReferencePayload } from '@/types/payloads'

export interface LabResultListParams {
  page?: number
  size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  date_from?: string
  date_to?: string
}

export interface BiomarkerTrendPoint {
  date: string
  value: number
  ref_min: number | null
  ref_max: number | null
  is_normal: boolean | null
}

export async function listLabResults(params?: LabResultListParams): Promise<PaginatedResponse<LabResult>> {
  const response = await apiClient.get('/api/v1/lab-results/', { params })
  return response.data
}

export async function getLabResult(id: number): Promise<LabResult> {
  const response = await apiClient.get(`/api/v1/lab-results/${id}`)
  return response.data
}

export async function createLabResult(data: LabResultPayload): Promise<LabResult> {
  const response = await apiClient.post('/api/v1/lab-results/', data)
  return response.data
}

export async function updateLabResult(id: number, data: Partial<LabResultPayload>): Promise<LabResult> {
  const response = await apiClient.put(`/api/v1/lab-results/${id}`, data)
  return response.data
}

export async function deleteLabResult(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/lab-results/${id}`)
}

export async function getBiomarkerTrend(biomarkerName: string): Promise<BiomarkerTrendPoint[]> {
  const response = await apiClient.get('/api/v1/lab-results/biomarker-trend', {
    params: { biomarker_name: biomarkerName },
  })
  return response.data
}

// Biomarker references
export async function listBiomarkerReferences(search?: string): Promise<BiomarkerReference[]> {
  if (isDemoMode.value) {
    let items = demo().getBiomarkers()
    if (search) {
      const q = search.toLowerCase()
      items = items.filter((b) => b.name.toLowerCase().includes(q))
    }
    return items
  }
  const response = await apiClient.get('/api/v1/biomarker-references/', {
    params: search ? { search } : {},
  })
  return response.data
}

export async function createBiomarkerReference(data: BiomarkerReferencePayload): Promise<BiomarkerReference> {
  const response = await apiClient.post('/api/v1/biomarker-references/', data)
  return response.data
}

export async function updateBiomarkerReference(id: number, data: Partial<BiomarkerReferencePayload>): Promise<BiomarkerReference> {
  const response = await apiClient.put(`/api/v1/biomarker-references/${id}`, data)
  return response.data
}

export async function deleteBiomarkerReference(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/biomarker-references/${id}`)
}

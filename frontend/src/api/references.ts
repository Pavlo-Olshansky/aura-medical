import { apiClient } from '@/api/client'
import type { Reference } from '@/types'

export type ReferenceResource = 'positions' | 'procedures' | 'clinics' | 'cities'

export async function listResource(resource: ReferenceResource, search?: string, sort?: string): Promise<Reference[]> {
  const params: Record<string, string> = {}
  if (search) params.search = search
  if (sort) params.sort = sort
  const response = await apiClient.get(`/api/v1/${resource}/`, { params })
  return response.data
}

export async function createResource(resource: ReferenceResource, name: string): Promise<Reference> {
  const response = await apiClient.post(`/api/v1/${resource}/`, { name })
  return response.data
}

export async function updateResource(resource: ReferenceResource, id: number, name: string): Promise<Reference> {
  const response = await apiClient.put(`/api/v1/${resource}/${id}`, { name })
  return response.data
}

export async function deleteResource(resource: ReferenceResource, id: number): Promise<void> {
  await apiClient.delete(`/api/v1/${resource}/${id}`)
}

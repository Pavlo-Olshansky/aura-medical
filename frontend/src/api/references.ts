import { apiClient } from '@/api/client'
import type { Reference } from '@/types'

export type ReferenceResource = 'positions' | 'procedures' | 'clinics' | 'cities'

export async function listResource(resource: ReferenceResource, search?: string): Promise<Reference[]> {
  const params: Record<string, string> = {}
  if (search) {
    params.search = search
  }
  const response = await apiClient.get(`/api/${resource}/`, { params })
  return response.data
}

export async function createResource(resource: ReferenceResource, name: string): Promise<Reference> {
  const response = await apiClient.post(`/api/${resource}/`, { name })
  return response.data
}

export async function updateResource(resource: ReferenceResource, id: number, name: string): Promise<Reference> {
  const response = await apiClient.put(`/api/${resource}/${id}`, { name })
  return response.data
}

export async function deleteResource(resource: ReferenceResource, id: number): Promise<void> {
  await apiClient.delete(`/api/${resource}/${id}`)
}

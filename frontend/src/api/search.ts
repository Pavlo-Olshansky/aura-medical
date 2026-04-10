import { apiClient } from '@/api/client'
import type { SearchResponse } from '@/types'

export async function globalSearch(q: string, limit: number = 5): Promise<SearchResponse> {
  const response = await apiClient.get('/api/v1/search/', { params: { q, limit } })
  return response.data
}

import { apiClient } from '@/api/client'
import type { TimelineEvent, PaginatedResponse } from '@/types'

export interface TimelineListParams {
  page?: number
  size?: number
  event_type?: 'visit' | 'treatment' | 'lab_result' | 'vaccination'
  date_from?: string
  date_to?: string
}

export async function listTimeline(params?: TimelineListParams): Promise<PaginatedResponse<TimelineEvent>> {
  const response = await apiClient.get('/api/timeline/', { params })
  return response.data
}

import { apiClient } from './client'

export interface Reminder {
  entity_type: string
  entity_id: number
  reminder_type: string
  title: string
  event_date: string
  route: string
}

export interface RemindersResponse {
  items: Reminder[]
  count: number
}

export interface DismissRequest {
  entity_type: string
  entity_id: number
  reminder_type: string
}

export async function listReminders(): Promise<RemindersResponse> {
  const { data } = await apiClient.get<RemindersResponse>('/api/v1/notifications/')
  return data
}

export async function dismissReminder(req: DismissRequest): Promise<void> {
  await apiClient.post('/api/v1/notifications/dismiss', req)
}

import { apiClient } from '@/api/client'
import type { CalendarEventsResponse } from '@/types'

export async function getCalendarEvents(dateFrom: string, dateTo: string): Promise<CalendarEventsResponse> {
  const response = await apiClient.get('/api/v1/calendar/events', {
    params: { date_from: dateFrom, date_to: dateTo },
  })
  return response.data
}

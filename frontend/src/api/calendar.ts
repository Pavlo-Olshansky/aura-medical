import { apiClient } from '@/api/client'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import type { CalendarEventsResponse } from '@/types'

export async function getCalendarEvents(dateFrom: string, dateTo: string): Promise<CalendarEventsResponse> {
  if (isDemoMode.value) {
    return {
      events: demo().getCalendarEvents(dateFrom, dateTo),
      date_from: dateFrom,
      date_to: dateTo,
    }
  }
  const response = await apiClient.get('/api/v1/calendar/events', {
    params: { date_from: dateFrom, date_to: dateTo },
  })
  return response.data
}

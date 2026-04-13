import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CalendarEvent } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import { getCalendarEvents } from '@/api/calendar'

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<CalendarEvent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchEvents(dateFrom: string, dateTo: string) {
    if (isDemoMode.value) {
      events.value = demo().getCalendarEvents(dateFrom, dateTo)
      return
    }
    loading.value = true
    error.value = null
    try {
      const data = await getCalendarEvents(dateFrom, dateTo)
      events.value = data.events
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження подій календаря')
      throw e
    } finally {
      loading.value = false
    }
  }

  return { events, loading, error, fetchEvents }
})

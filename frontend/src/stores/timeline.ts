import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TimelineEvent, PaginatedResponse } from '@/types'
import {
  listTimeline as apiListTimeline,
  type TimelineListParams,
} from '@/api/timeline'

export const useTimelineStore = defineStore('timeline', () => {
  const events = ref<TimelineEvent[]>([])
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTimeline(params?: TimelineListParams) {
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<TimelineEvent> = await apiListTimeline(params)
      events.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка завантаження хронології'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    events,
    total,
    page,
    size,
    pages,
    loading,
    error,
    fetchTimeline,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Visit, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import {
  listVisits as apiListVisits,
  getVisit as apiGetVisit,
  createVisit as apiCreateVisit,
  updateVisit as apiUpdateVisit,
  deleteVisit as apiDeleteVisit,
  type VisitListParams,
} from '@/api/visits'

export const useVisitsStore = defineStore('visits', () => {
  const visits = ref<Visit[]>([])
  const currentVisit = ref<Visit | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchVisits(params?: VisitListParams) {
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Visit> = await apiListVisits(params)
      visits.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження візитів')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchVisit(id: number) {
    loading.value = true
    error.value = null
    try {
      currentVisit.value = await apiGetVisit(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createVisit(formData: FormData) {
    loading.value = true
    error.value = null
    try {
      const visit = await apiCreateVisit(formData)
      return visit
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateVisit(id: number, formData: FormData) {
    loading.value = true
    error.value = null
    try {
      const visit = await apiUpdateVisit(id, formData)
      currentVisit.value = visit
      return visit
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteVisit(id: number) {
    loading.value = true
    error.value = null
    try {
      await apiDeleteVisit(id)
      currentVisit.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    visits,
    currentVisit,
    total,
    page,
    size,
    pages,
    loading,
    error,
    fetchVisits,
    fetchVisit,
    createVisit,
    updateVisit,
    deleteVisit,
  }
})

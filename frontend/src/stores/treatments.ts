import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Treatment, PaginatedResponse } from '@/types'
import {
  listTreatments as apiListTreatments,
  getTreatment as apiGetTreatment,
  createTreatment as apiCreateTreatment,
  updateTreatment as apiUpdateTreatment,
  deleteTreatment as apiDeleteTreatment,
  type TreatmentListParams,
  type TreatmentPayload,
} from '@/api/treatments'

export const useTreatmentsStore = defineStore('treatments', () => {
  const treatments = ref<Treatment[]>([])
  const currentTreatment = ref<Treatment | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTreatments(params?: TreatmentListParams) {
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Treatment> = await apiListTreatments(params)
      treatments.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка завантаження лікувань'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTreatment(id: number) {
    loading.value = true
    error.value = null
    try {
      currentTreatment.value = await apiGetTreatment(id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка завантаження лікування'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createTreatment(data: TreatmentPayload) {
    loading.value = true
    error.value = null
    try {
      const treatment = await apiCreateTreatment(data)
      return treatment
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка створення лікування'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTreatment(id: number, data: TreatmentPayload) {
    loading.value = true
    error.value = null
    try {
      const treatment = await apiUpdateTreatment(id, data)
      currentTreatment.value = treatment
      return treatment
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка оновлення лікування'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteTreatment(id: number) {
    loading.value = true
    error.value = null
    try {
      await apiDeleteTreatment(id)
      currentTreatment.value = null
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка видалення лікування'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    treatments,
    currentTreatment,
    total,
    page,
    size,
    pages,
    loading,
    error,
    fetchTreatments,
    fetchTreatment,
    createTreatment,
    updateTreatment,
    deleteTreatment,
  }
})

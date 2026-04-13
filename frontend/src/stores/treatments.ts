import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Treatment, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import {
  listTreatments as apiListTreatments,
  getTreatment as apiGetTreatment,
  createTreatment as apiCreateTreatment,
  updateTreatment as apiUpdateTreatment,
  deleteTreatment as apiDeleteTreatment,
  type TreatmentListParams,
  type TreatmentPayload,
} from '@/api/treatments'

function treatmentFromPayload(data: TreatmentPayload): Omit<Treatment, 'id'> {
  const now = new Date().toISOString()
  const start = new Date(data.date_start)
  const end = new Date(start.getTime() + data.days * 86_400_000)
  const status: Treatment['status'] = end < new Date() ? 'completed' : 'active'
  return {
    date_start: data.date_start,
    name: data.name,
    days: data.days,
    receipt: data.receipt ?? '',
    status,
    body_region: data.body_region ?? null,
    created: now,
    updated: now,
  }
}

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
    if (isDemoMode.value) {
      const all = demo().getTreatments()
      const pageNum = params?.page ?? 1
      const sizeNum = params?.size ?? 20
      const start = (pageNum - 1) * sizeNum
      treatments.value = all.slice(start, start + sizeNum)
      total.value = all.length
      page.value = pageNum
      size.value = sizeNum
      pages.value = Math.max(1, Math.ceil(all.length / sizeNum))
      return
    }
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Treatment> = await apiListTreatments(params)
      treatments.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження лікувань')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTreatment(id: number) {
    if (isDemoMode.value) {
      currentTreatment.value = demo().getTreatments().find((t) => t.id === id) ?? null
      return
    }
    loading.value = true
    error.value = null
    try {
      currentTreatment.value = await apiGetTreatment(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження лікування')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createTreatment(data: TreatmentPayload) {
    if (isDemoMode.value) {
      const created = demo().create(demo().getTreatments(), treatmentFromPayload(data))
      treatments.value = [...demo().getTreatments()]
      return created
    }
    loading.value = true
    error.value = null
    try {
      const treatment = await apiCreateTreatment(data)
      return treatment
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення лікування')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTreatment(id: number, data: TreatmentPayload) {
    if (isDemoMode.value) {
      const updated = demo().update(demo().getTreatments(), id, treatmentFromPayload(data))
      if (updated) currentTreatment.value = updated
      treatments.value = [...demo().getTreatments()]
      return updated as Treatment
    }
    loading.value = true
    error.value = null
    try {
      const treatment = await apiUpdateTreatment(id, data)
      currentTreatment.value = treatment
      return treatment
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення лікування')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteTreatment(id: number) {
    if (isDemoMode.value) {
      demo().remove(demo().getTreatments(), id)
      treatments.value = [...demo().getTreatments()]
      currentTreatment.value = null
      return
    }
    loading.value = true
    error.value = null
    try {
      await apiDeleteTreatment(id)
      currentTreatment.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення лікування')
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

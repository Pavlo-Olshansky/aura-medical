import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Vaccination, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import {
  listVaccinations as apiListVaccinations,
  getVaccination as apiGetVaccination,
  createVaccination as apiCreateVaccination,
  updateVaccination as apiUpdateVaccination,
  deleteVaccination as apiDeleteVaccination,
  type VaccinationListParams,
} from '@/api/vaccinations'

function vaccinationFromFormData(formData: FormData): Omit<Vaccination, 'id'> {
  const now = new Date().toISOString()
  const get = (k: string) => {
    const v = formData.get(k)
    return typeof v === 'string' && v.length > 0 ? v : null
  }
  const date = get('date') ?? now.slice(0, 10)
  const days = get('next_due_date')
  const today = new Date()
  const dueDate = days ? new Date(days) : null
  let status: Vaccination['status'] = 'completed'
  if (dueDate) status = dueDate < today ? 'overdue' : 'upcoming'
  return {
    date,
    vaccine_name: get('vaccine_name') ?? '',
    manufacturer: get('manufacturer'),
    lot_number: get('lot_number'),
    dose_number: Number(get('dose_number') ?? 1),
    next_due_date: days,
    notes: get('notes'),
    has_document: false,
    status,
    created: now,
    updated: now,
  }
}

export const useVaccinationsStore = defineStore('vaccinations', () => {
  const vaccinations = ref<Vaccination[]>([])
  const currentVaccination = ref<Vaccination | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchVaccinations(params?: VaccinationListParams) {
    if (isDemoMode.value) {
      let all = demo().getVaccinations()
      if (params?.status) all = all.filter((v) => v.status === params.status)
      const pageNum = params?.page ?? 1
      const sizeNum = params?.size ?? 20
      const start = (pageNum - 1) * sizeNum
      vaccinations.value = all.slice(start, start + sizeNum)
      total.value = all.length
      page.value = pageNum
      size.value = sizeNum
      pages.value = Math.max(1, Math.ceil(all.length / sizeNum))
      return
    }
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Vaccination> = await apiListVaccinations(params)
      vaccinations.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження вакцинацій')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchVaccination(id: number) {
    if (isDemoMode.value) {
      currentVaccination.value = demo().getVaccinations().find((v) => v.id === id) ?? null
      return
    }
    loading.value = true
    error.value = null
    try {
      currentVaccination.value = await apiGetVaccination(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження вакцинації')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createVaccination(formData: FormData) {
    if (isDemoMode.value) {
      const created = demo().create(demo().getVaccinations(), vaccinationFromFormData(formData))
      vaccinations.value = [...demo().getVaccinations()]
      return created
    }
    loading.value = true
    error.value = null
    try {
      const vaccination = await apiCreateVaccination(formData)
      return vaccination
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення вакцинації')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateVaccination(id: number, formData: FormData) {
    if (isDemoMode.value) {
      const updated = demo().update(demo().getVaccinations(), id, vaccinationFromFormData(formData))
      if (updated) currentVaccination.value = updated
      vaccinations.value = [...demo().getVaccinations()]
      return updated as Vaccination
    }
    loading.value = true
    error.value = null
    try {
      const vaccination = await apiUpdateVaccination(id, formData)
      currentVaccination.value = vaccination
      return vaccination
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення вакцинації')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteVaccination(id: number) {
    if (isDemoMode.value) {
      demo().remove(demo().getVaccinations(), id)
      vaccinations.value = [...demo().getVaccinations()]
      currentVaccination.value = null
      return
    }
    loading.value = true
    error.value = null
    try {
      await apiDeleteVaccination(id)
      currentVaccination.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення вакцинації')
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    vaccinations,
    currentVaccination,
    total,
    page,
    size,
    pages,
    loading,
    error,
    fetchVaccinations,
    fetchVaccination,
    createVaccination,
    updateVaccination,
    deleteVaccination,
  }
})

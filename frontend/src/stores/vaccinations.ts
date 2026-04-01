import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Vaccination, PaginatedResponse } from '@/types'
import {
  listVaccinations as apiListVaccinations,
  getVaccination as apiGetVaccination,
  createVaccination as apiCreateVaccination,
  updateVaccination as apiUpdateVaccination,
  deleteVaccination as apiDeleteVaccination,
  type VaccinationListParams,
} from '@/api/vaccinations'

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
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Vaccination> = await apiListVaccinations(params)
      vaccinations.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка завантаження вакцинацій'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchVaccination(id: number) {
    loading.value = true
    error.value = null
    try {
      currentVaccination.value = await apiGetVaccination(id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка завантаження вакцинації'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createVaccination(formData: FormData) {
    loading.value = true
    error.value = null
    try {
      const vaccination = await apiCreateVaccination(formData)
      return vaccination
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка створення вакцинації'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateVaccination(id: number, formData: FormData) {
    loading.value = true
    error.value = null
    try {
      const vaccination = await apiUpdateVaccination(id, formData)
      currentVaccination.value = vaccination
      return vaccination
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка оновлення вакцинації'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteVaccination(id: number) {
    loading.value = true
    error.value = null
    try {
      await apiDeleteVaccination(id)
      currentVaccination.value = null
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Помилка видалення вакцинації'
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

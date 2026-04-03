import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LabResult, BiomarkerReference, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import {
  listLabResults as apiListLabResults,
  getLabResult as apiGetLabResult,
  createLabResult as apiCreateLabResult,
  updateLabResult as apiUpdateLabResult,
  deleteLabResult as apiDeleteLabResult,
  getBiomarkerTrend as apiGetBiomarkerTrend,
  listBiomarkerReferences as apiListBiomarkerReferences,
  type LabResultListParams,
  type BiomarkerTrendPoint,
} from '@/api/labResults'

export const useLabResultsStore = defineStore('labResults', () => {
  const labResults = ref<LabResult[]>([])
  const currentLabResult = ref<LabResult | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const biomarkerReferences = ref<BiomarkerReference[]>([])

  async function fetchLabResults(params?: LabResultListParams) {
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<LabResult> = await apiListLabResults(params)
      labResults.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження результатів аналізів')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchLabResult(id: number) {
    loading.value = true
    error.value = null
    try {
      currentLabResult.value = await apiGetLabResult(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження результату аналізу')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createLabResult(data: any) {
    loading.value = true
    error.value = null
    try {
      const labResult = await apiCreateLabResult(data)
      return labResult
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення результату аналізу')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateLabResult(id: number, data: any) {
    loading.value = true
    error.value = null
    try {
      const labResult = await apiUpdateLabResult(id, data)
      currentLabResult.value = labResult
      return labResult
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення результату аналізу')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteLabResult(id: number) {
    loading.value = true
    error.value = null
    try {
      await apiDeleteLabResult(id)
      currentLabResult.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення результату аналізу')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchBiomarkerTrend(biomarkerName: string): Promise<BiomarkerTrendPoint[]> {
    loading.value = true
    error.value = null
    try {
      return await apiGetBiomarkerTrend(biomarkerName)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження тренду біомаркера')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchBiomarkerReferences(search?: string) {
    loading.value = true
    error.value = null
    try {
      biomarkerReferences.value = await apiListBiomarkerReferences(search)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження довідника біомаркерів')
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    labResults,
    currentLabResult,
    total,
    page,
    size,
    pages,
    loading,
    error,
    biomarkerReferences,
    fetchLabResults,
    fetchLabResult,
    createLabResult,
    updateLabResult,
    deleteLabResult,
    fetchBiomarkerTrend,
    fetchBiomarkerReferences,
  }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LabResult, BiomarkerReference, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo, demoSort } from '@/stores/demoRegistry'
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
    if (isDemoMode.value) {
      let all = demo().getLabResults()
      if (params?.date_from) all = all.filter((r) => r.date >= params.date_from!)
      if (params?.date_to) all = all.filter((r) => r.date <= params.date_to!)
      all = demoSort(all, params?.sort_by ?? 'date', params?.sort_order ?? 'desc')
      const pageNum = params?.page ?? 1
      const sizeNum = params?.size ?? 20
      const start = (pageNum - 1) * sizeNum
      labResults.value = all.slice(start, start + sizeNum)
      total.value = all.length
      page.value = pageNum
      size.value = sizeNum
      pages.value = Math.max(1, Math.ceil(all.length / sizeNum))
      return
    }
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
    if (isDemoMode.value) {
      currentLabResult.value = demo().getLabResults().find((r) => r.id === id) ?? null
      return
    }
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
    if (isDemoMode.value) {
      const now = new Date().toISOString()
      const created = demo().create(demo().getLabResults(), {
        date: data?.date ?? now.slice(0, 10),
        visit_id: data?.visit_id ?? null,
        notes: data?.notes ?? null,
        entries: data?.entries ?? [],
        entries_count: data?.entries?.length ?? 0,
        out_of_range_count: 0,
        visit_date: undefined,
        visit_procedure: undefined,
        created: now,
        updated: now,
      })
      labResults.value = [...demo().getLabResults()]
      return created
    }
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
    if (isDemoMode.value) {
      const updated = demo().update(demo().getLabResults(), id, {
        ...data,
        updated: new Date().toISOString(),
      })
      if (updated) currentLabResult.value = updated
      labResults.value = [...demo().getLabResults()]
      return updated as LabResult
    }
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
    if (isDemoMode.value) {
      demo().remove(demo().getLabResults(), id)
      labResults.value = [...demo().getLabResults()]
      currentLabResult.value = null
      return
    }
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
    if (isDemoMode.value) {
      // Synthesize a trend from existing demo lab entries matching the name.
      const points: BiomarkerTrendPoint[] = []
      for (const result of demo().getLabResults()) {
        for (const entry of result.entries) {
          if (entry.biomarker_name === biomarkerName) {
            points.push({
              date: result.date,
              value: entry.value,
              ref_min: entry.ref_min,
              ref_max: entry.ref_max,
              is_normal: entry.is_normal,
            })
          }
        }
      }
      return points.sort((a, b) => a.date.localeCompare(b.date))
    }
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
    if (isDemoMode.value) {
      let items = demo().getBiomarkers()
      if (search) {
        const q = search.toLowerCase()
        items = items.filter((b) => b.name.toLowerCase().includes(q))
      }
      biomarkerReferences.value = items
      return
    }
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

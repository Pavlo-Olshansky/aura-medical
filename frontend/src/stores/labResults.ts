import { defineStore, storeToRefs } from 'pinia'
import { ref } from 'vue'
import type { LabResult, BiomarkerReference } from '@/types'
import type { LabResultPayload } from '@/types/payloads'
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
  type BiomarkerTrendPoint,
} from '@/api/labResults'
import { createEntityStore } from '@/stores/factory/useDataStore'

function labResultFromPayload(data: LabResultPayload): Omit<LabResult, 'id'> {
  const now = new Date().toISOString()
  const entries = (data.entries ?? []).map((e, i) => ({
    id: -(i + 1),
    biomarker_id: e.biomarker_id ?? null,
    biomarker_name: e.biomarker_name,
    value: e.value,
    unit: e.unit,
    ref_min: e.ref_min ?? null,
    ref_max: e.ref_max ?? null,
    is_normal: e.ref_min != null && e.ref_max != null
      ? e.value >= e.ref_min && e.value <= e.ref_max
      : null,
  }))
  return {
    date: data.date,
    visit_id: data.visit_id ?? null,
    notes: data.notes ?? null,
    entries,
    entries_count: entries.length,
    out_of_range_count: entries.filter((e) => e.is_normal === false).length,
    visit_date: undefined,
    visit_procedure: undefined,
    created: now,
    updated: now,
  }
}

const _useBaseStore = createEntityStore<LabResult, LabResultPayload, Partial<LabResultPayload>>({
  id: 'labResults-base',
  api: {
    list: apiListLabResults,
    get: apiGetLabResult,
    create: apiCreateLabResult,
    update: apiUpdateLabResult,
    delete: apiDeleteLabResult,
  },
  demo: {
    list: (params) => {
      let all = demo().getLabResults()
      if (params?.date_from) all = all.filter((r) => r.date >= (params.date_from as string))
      if (params?.date_to) all = all.filter((r) => r.date <= (params.date_to as string))
      all = demoSort(all, (params?.sort_by as string) ?? 'date', (params?.sort_order as 'asc' | 'desc') ?? 'desc')
      const pageNum = (params?.page as number) ?? 1
      const sizeNum = (params?.size as number) ?? 20
      const start = (pageNum - 1) * sizeNum
      return {
        items: all.slice(start, start + sizeNum),
        total: all.length,
        page: pageNum,
        size: sizeNum,
        pages: Math.max(1, Math.ceil(all.length / sizeNum)),
      }
    },
    get: (id) => demo().getLabResults().find((r) => r.id === id),
    create: (data) => demo().create(demo().getLabResults(), labResultFromPayload(data)),
    update: (id, data) => {
      const patch: Partial<LabResult> = { updated: new Date().toISOString() }
      if (data.date !== undefined) patch.date = data.date
      if (data.visit_id !== undefined) patch.visit_id = data.visit_id ?? null
      if (data.notes !== undefined) patch.notes = data.notes ?? null
      if (data.entries !== undefined) {
        patch.entries = data.entries.map((e, i) => ({
          id: -(i + 1),
          biomarker_id: e.biomarker_id ?? null,
          biomarker_name: e.biomarker_name,
          value: e.value,
          unit: e.unit,
          ref_min: e.ref_min ?? null,
          ref_max: e.ref_max ?? null,
          is_normal: e.ref_min != null && e.ref_max != null
            ? e.value >= e.ref_min && e.value <= e.ref_max
            : null,
        }))
        patch.entries_count = patch.entries.length
        patch.out_of_range_count = patch.entries.filter((e) => e.is_normal === false).length
      }
      return demo().update(demo().getLabResults(), id, patch)
    },
    delete: (id) => demo().remove(demo().getLabResults(), id),
  },
  errorMessages: {
    list: 'Помилка завантаження результатів аналізів',
    get: 'Помилка завантаження результату аналізу',
    create: 'Помилка створення результату аналізу',
    update: 'Помилка оновлення результату аналізу',
    delete: 'Помилка видалення результату аналізу',
  },
})

export const useLabResultsStore = defineStore('labResults', () => {
  const base = _useBaseStore()
  const {
    items, currentItem, total, page, size, pages, loading, error,
  } = storeToRefs(base)

  const biomarkerReferences = ref<BiomarkerReference[]>([])

  async function fetchBiomarkerTrend(biomarkerName: string): Promise<BiomarkerTrendPoint[]> {
    if (isDemoMode.value) {
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
    items,
    currentItem,
    total,
    page,
    size,
    pages,
    loading,
    error,
    biomarkerReferences,
    fetchList: base.fetchList,
    fetchOne: base.fetchOne,
    create: base.create,
    update: base.update,
    remove: base.remove,
    fetchBiomarkerTrend,
    fetchBiomarkerReferences,
  }
})

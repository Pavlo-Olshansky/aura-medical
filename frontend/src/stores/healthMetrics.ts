import { defineStore, storeToRefs } from 'pinia'
import { ref } from 'vue'
import type { HealthMetric, MetricType } from '@/types'
import type { HealthMetricPayload } from '@/types/payloads'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo, demoSort } from '@/stores/demoRegistry'
import {
  listHealthMetrics as apiListHealthMetrics,
  getHealthMetric as apiGetHealthMetric,
  createHealthMetric as apiCreateHealthMetric,
  updateHealthMetric as apiUpdateHealthMetric,
  deleteHealthMetric as apiDeleteHealthMetric,
  getMetricTrend as apiGetMetricTrend,
  listMetricTypes as apiListMetricTypes,
  type MetricTrendParams,
  type MetricTrendPoint,
} from '@/api/healthMetrics'
import { createEntityStore } from '@/stores/factory/useDataStore'

function healthMetricFromPayload(data: HealthMetricPayload): Omit<HealthMetric, 'id'> {
  const now = new Date().toISOString()
  const type = demo().getMetricTypes().find((t) => t.id === data.metric_type_id)
  const fallbackType = demo().getMetricTypes()[0]!
  return {
    metric_type_id: data.metric_type_id,
    metric_type: type ?? fallbackType,
    date: data.date,
    value: data.value,
    secondary_value: data.secondary_value ?? null,
    notes: data.notes ?? null,
    created: now,
    updated: now,
  }
}

const _useBaseStore = createEntityStore<HealthMetric, HealthMetricPayload, Partial<HealthMetricPayload>>({
  id: 'healthMetrics-base',
  api: {
    list: apiListHealthMetrics,
    get: apiGetHealthMetric,
    create: apiCreateHealthMetric,
    update: apiUpdateHealthMetric,
    delete: apiDeleteHealthMetric,
  },
  demo: {
    list: (params) => {
      let all = demo().getHealthMetrics()
      if (params?.metric_type_id) all = all.filter((m) => m.metric_type_id === params.metric_type_id)
      if (params?.date_from) all = all.filter((m) => m.date >= (params.date_from as string))
      if (params?.date_to) all = all.filter((m) => m.date <= (params.date_to as string))
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
    get: (id) => demo().getHealthMetrics().find((m) => m.id === id),
    create: (data) => demo().create(demo().getHealthMetrics(), healthMetricFromPayload(data)),
    update: (id, data) => {
      return demo().update(demo().getHealthMetrics(), id, {
        ...data,
        updated: new Date().toISOString(),
      })
    },
    delete: (id) => demo().remove(demo().getHealthMetrics(), id),
  },
  errorMessages: {
    list: 'Помилка завантаження показників здоров\'я',
    get: 'Помилка завантаження показника здоров\'я',
    create: 'Помилка створення показника здоров\'я',
    update: 'Помилка оновлення показника здоров\'я',
    delete: 'Помилка видалення показника здоров\'я',
  },
})

export const useHealthMetricsStore = defineStore('healthMetrics', () => {
  const base = _useBaseStore()
  const {
    items, currentItem, total, page, size, pages, loading, error,
  } = storeToRefs(base)

  const metricTypes = ref<MetricType[]>([])

  async function fetchMetricTrend(params: MetricTrendParams): Promise<MetricTrendPoint[]> {
    if (isDemoMode.value) {
      return demo()
        .getHealthMetrics()
        .filter((m) => m.metric_type_id === params.metric_type_id)
        .filter((m) => (!params.date_from || m.date >= params.date_from) && (!params.date_to || m.date <= params.date_to))
        .sort((a, b) => a.date.localeCompare(b.date))
        .map((m) => ({ date: m.date, value: m.value, secondary_value: m.secondary_value }))
    }
    loading.value = true
    error.value = null
    try {
      return await apiGetMetricTrend(params)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження тренду показника')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchMetricTypes(search?: string) {
    if (isDemoMode.value) {
      let items = demo().getMetricTypes()
      if (search) {
        const q = search.toLowerCase()
        items = items.filter((t) => t.name.toLowerCase().includes(q))
      }
      metricTypes.value = items
      return
    }
    loading.value = true
    error.value = null
    try {
      metricTypes.value = await apiListMetricTypes(search)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження типів показників')
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
    metricTypes,
    fetchList: base.fetchList,
    fetchOne: base.fetchOne,
    create: base.create,
    update: base.update,
    remove: base.remove,
    fetchMetricTrend,
    fetchMetricTypes,
  }
})

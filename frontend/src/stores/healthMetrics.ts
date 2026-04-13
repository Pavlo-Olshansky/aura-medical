import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HealthMetric, MetricType, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import {
  listHealthMetrics as apiListHealthMetrics,
  getHealthMetric as apiGetHealthMetric,
  createHealthMetric as apiCreateHealthMetric,
  updateHealthMetric as apiUpdateHealthMetric,
  deleteHealthMetric as apiDeleteHealthMetric,
  getMetricTrend as apiGetMetricTrend,
  listMetricTypes as apiListMetricTypes,
  type HealthMetricListParams,
  type MetricTrendParams,
  type MetricTrendPoint,
} from '@/api/healthMetrics'

export const useHealthMetricsStore = defineStore('healthMetrics', () => {
  const healthMetrics = ref<HealthMetric[]>([])
  const currentMetric = ref<HealthMetric | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const metricTypes = ref<MetricType[]>([])

  async function fetchHealthMetrics(params?: HealthMetricListParams) {
    if (isDemoMode.value) {
      let all = demo().getHealthMetrics()
      if (params?.metric_type_id) {
        all = all.filter((m) => m.metric_type_id === params.metric_type_id)
      }
      const pageNum = params?.page ?? 1
      const sizeNum = params?.size ?? 20
      const start = (pageNum - 1) * sizeNum
      healthMetrics.value = all.slice(start, start + sizeNum)
      total.value = all.length
      page.value = pageNum
      size.value = sizeNum
      pages.value = Math.max(1, Math.ceil(all.length / sizeNum))
      return
    }
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<HealthMetric> = await apiListHealthMetrics(params)
      healthMetrics.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження показників здоров\'я')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchHealthMetric(id: number) {
    if (isDemoMode.value) {
      currentMetric.value = demo().getHealthMetrics().find((m) => m.id === id) ?? null
      return
    }
    loading.value = true
    error.value = null
    try {
      currentMetric.value = await apiGetHealthMetric(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження показника здоров\'я')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createHealthMetric(data: any) {
    if (isDemoMode.value) {
      const now = new Date().toISOString()
      const type = demo().getMetricTypes().find((t) => t.id === data?.metric_type_id)
      const fallbackType = demo().getMetricTypes()[0]!
      const created = demo().create(demo().getHealthMetrics(), {
        metric_type_id: data?.metric_type_id ?? 1,
        metric_type: type ?? fallbackType,
        date: data?.date ?? now.slice(0, 10),
        value: data?.value ?? 0,
        secondary_value: data?.secondary_value ?? null,
        notes: data?.notes ?? null,
        created: now,
        updated: now,
      })
      healthMetrics.value = [...demo().getHealthMetrics()]
      return created
    }
    loading.value = true
    error.value = null
    try {
      const metric = await apiCreateHealthMetric(data)
      return metric
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення показника здоров\'я')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateHealthMetric(id: number, data: any) {
    if (isDemoMode.value) {
      const updated = demo().update(demo().getHealthMetrics(), id, {
        ...data,
        updated: new Date().toISOString(),
      })
      if (updated) currentMetric.value = updated
      healthMetrics.value = [...demo().getHealthMetrics()]
      return updated as HealthMetric
    }
    loading.value = true
    error.value = null
    try {
      const metric = await apiUpdateHealthMetric(id, data)
      currentMetric.value = metric
      return metric
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення показника здоров\'я')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteHealthMetric(id: number) {
    if (isDemoMode.value) {
      demo().remove(demo().getHealthMetrics(), id)
      healthMetrics.value = [...demo().getHealthMetrics()]
      currentMetric.value = null
      return
    }
    loading.value = true
    error.value = null
    try {
      await apiDeleteHealthMetric(id)
      currentMetric.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення показника здоров\'я')
      throw e
    } finally {
      loading.value = false
    }
  }

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
    healthMetrics,
    currentMetric,
    total,
    page,
    size,
    pages,
    loading,
    error,
    metricTypes,
    fetchHealthMetrics,
    fetchHealthMetric,
    createHealthMetric,
    updateHealthMetric,
    deleteHealthMetric,
    fetchMetricTrend,
    fetchMetricTypes,
  }
})

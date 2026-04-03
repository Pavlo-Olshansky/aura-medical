import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HealthMetric, MetricType, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
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

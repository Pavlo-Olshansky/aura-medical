import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Visit, PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo, demoSort } from '@/stores/demoRegistry'
import {
  listVisits as apiListVisits,
  getVisit as apiGetVisit,
  createVisit as apiCreateVisit,
  updateVisit as apiUpdateVisit,
  deleteVisit as apiDeleteVisit,
  type VisitListParams,
} from '@/api/visits'

export const useVisitsStore = defineStore('visits', () => {
  const visits = ref<Visit[]>([])
  const currentVisit = ref<Visit | null>(null)
  const total = ref(0)
  const page = ref(1)
  const size = ref(20)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchVisits(params?: VisitListParams & { body_region?: string }) {
    if (isDemoMode.value) {
      let all = demo().getVisits()
      if (params?.date_from) all = all.filter((v) => v.date >= params.date_from!)
      if (params?.date_to) all = all.filter((v) => v.date <= params.date_to!)
      if (params?.clinic_id) all = all.filter((v) => v.clinic?.id === params.clinic_id)
      if (params?.city_id) all = all.filter((v) => v.city?.id === params.city_id)
      if (params?.procedure_id) all = all.filter((v) => v.procedure?.id === params.procedure_id)
      if (params?.position_id) all = all.filter((v) => v.position?.id === params.position_id)
      if (params?.body_region) all = all.filter((v) => v.body_region === params.body_region)
      all = demoSort(all, params?.sort_by ?? 'date', params?.sort_order ?? 'desc')
      const pageNum = params?.page ?? 1
      const sizeNum = params?.size ?? 20
      const start = (pageNum - 1) * sizeNum
      visits.value = all.slice(start, start + sizeNum)
      total.value = all.length
      page.value = pageNum
      size.value = sizeNum
      pages.value = Math.max(1, Math.ceil(all.length / sizeNum))
      return
    }
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<Visit> = await apiListVisits(params)
      visits.value = data.items
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження візитів')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchVisit(id: number) {
    if (isDemoMode.value) {
      currentVisit.value = demo().getVisits().find((v) => v.id === id) ?? null
      return
    }
    loading.value = true
    error.value = null
    try {
      currentVisit.value = await apiGetVisit(id)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createVisit(formData: FormData) {
    if (isDemoMode.value) {
      return createDemoVisit(formData)
    }
    loading.value = true
    error.value = null
    try {
      const visit = await apiCreateVisit(formData)
      return visit
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateVisit(id: number, formData: FormData) {
    if (isDemoMode.value) {
      return updateDemoVisit(id, formData)
    }
    loading.value = true
    error.value = null
    try {
      const visit = await apiUpdateVisit(id, formData)
      currentVisit.value = visit
      return visit
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteVisit(id: number) {
    if (isDemoMode.value) {
      demo().remove(demo().getVisits(), id)
      visits.value = [...demo().getVisits()]
      currentVisit.value = null
      return
    }
    loading.value = true
    error.value = null
    try {
      await apiDeleteVisit(id)
      currentVisit.value = null
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення візиту')
      throw e
    } finally {
      loading.value = false
    }
  }

  function visitFromFormData(formData: FormData): Omit<Visit, 'id'> {
    const now = new Date().toISOString()
    const get = (k: string) => {
      const v = formData.get(k)
      return typeof v === 'string' && v.length > 0 ? v : null
    }
    const file = formData.get('document')
    const documentName = file instanceof File ? file.name : null
    return {
      date: get('date') ?? now.slice(0, 10),
      position: null,
      doctor: get('doctor'),
      procedure: null,
      procedure_details: get('procedure_details'),
      clinic: null,
      city: null,
      document: documentName,
      has_document: !!documentName,
      body_region: get('body_region'),
      link: get('link'),
      comment: get('comment'),
      price: get('price') ? Number(get('price')) : null,
      created: now,
      updated: now,
    }
  }

  function createDemoVisit(formData: FormData): Visit {
    const created = demo().create(demo().getVisits(), visitFromFormData(formData))
    visits.value = [...demo().getVisits()]
    return created
  }

  function updateDemoVisit(id: number, formData: FormData): Visit | null {
    const updated = demo().update(demo().getVisits(), id, visitFromFormData(formData))
    if (updated) currentVisit.value = updated
    visits.value = [...demo().getVisits()]
    return updated ?? null
  }

  return {
    visits,
    currentVisit,
    total,
    page,
    size,
    pages,
    loading,
    error,
    fetchVisits,
    fetchVisit,
    createVisit,
    updateVisit,
    deleteVisit,
  }
})

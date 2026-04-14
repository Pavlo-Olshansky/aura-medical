import type { Visit } from '@/types'
import { demo, demoSort } from '@/stores/demoRegistry'
import {
  listVisits as apiListVisits,
  getVisit as apiGetVisit,
  createVisit as apiCreateVisit,
  updateVisit as apiUpdateVisit,
  deleteVisit as apiDeleteVisit,
} from '@/api/visits'
import { createEntityStore } from '@/stores/factory/useDataStore'

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

export const useVisitsStore = createEntityStore<Visit, FormData, FormData>({
  id: 'visits',
  api: {
    list: apiListVisits,
    get: apiGetVisit,
    create: apiCreateVisit,
    update: apiUpdateVisit,
    delete: apiDeleteVisit,
  },
  demo: {
    list: (params) => {
      let all = demo().getVisits()
      if (params?.date_from) all = all.filter((v) => v.date >= (params.date_from as string))
      if (params?.date_to) all = all.filter((v) => v.date <= (params.date_to as string))
      if (params?.clinic_id) all = all.filter((v) => v.clinic?.id === params.clinic_id)
      if (params?.city_id) all = all.filter((v) => v.city?.id === params.city_id)
      if (params?.procedure_id) all = all.filter((v) => v.procedure?.id === params.procedure_id)
      if (params?.position_id) all = all.filter((v) => v.position?.id === params.position_id)
      if (params?.body_region) all = all.filter((v) => v.body_region === params.body_region)
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
    get: (id) => demo().getVisits().find((v) => v.id === id),
    create: (formData) => {
      const created = demo().create(demo().getVisits(), visitFromFormData(formData))
      return created
    },
    update: (id, formData) => {
      const updated = demo().update(demo().getVisits(), id, visitFromFormData(formData))
      return updated
    },
    delete: (id) => demo().remove(demo().getVisits(), id),
  },
  errorMessages: {
    list: 'Помилка завантаження візитів',
    get: 'Помилка завантаження візиту',
    create: 'Помилка створення візиту',
    update: 'Помилка оновлення візиту',
    delete: 'Помилка видалення візиту',
  },
})

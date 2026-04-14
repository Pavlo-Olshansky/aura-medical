import type { Treatment } from '@/types'
import { demo } from '@/stores/demoRegistry'
import {
  listTreatments as apiListTreatments,
  getTreatment as apiGetTreatment,
  createTreatment as apiCreateTreatment,
  updateTreatment as apiUpdateTreatment,
  deleteTreatment as apiDeleteTreatment,
  type TreatmentPayload,
} from '@/api/treatments'
import { createEntityStore } from '@/stores/factory/useDataStore'

function treatmentFromPayload(data: TreatmentPayload): Omit<Treatment, 'id'> {
  const now = new Date().toISOString()
  const start = new Date(data.date_start)
  const end = new Date(start.getTime() + data.days * 86_400_000)
  const status: Treatment['status'] = end < new Date() ? 'completed' : 'active'
  return {
    date_start: data.date_start,
    name: data.name,
    days: data.days,
    receipt: data.receipt ?? '',
    status,
    body_region: data.body_region ?? null,
    created: now,
    updated: now,
  }
}

export const useTreatmentsStore = createEntityStore<Treatment, TreatmentPayload, TreatmentPayload>({
  id: 'treatments',
  api: {
    list: apiListTreatments,
    get: apiGetTreatment,
    create: apiCreateTreatment,
    update: apiUpdateTreatment,
    delete: apiDeleteTreatment,
  },
  demo: {
    list: (params) => {
      let all = demo().getTreatments()
      if (params?.status) all = all.filter((t) => t.status === params.status)
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
    get: (id) => demo().getTreatments().find((t) => t.id === id),
    create: (data) => demo().create(demo().getTreatments(), treatmentFromPayload(data)),
    update: (id, data) => demo().update(demo().getTreatments(), id, treatmentFromPayload(data)),
    delete: (id) => demo().remove(demo().getTreatments(), id),
  },
  errorMessages: {
    list: 'Помилка завантаження лікувань',
    get: 'Помилка завантаження лікування',
    create: 'Помилка створення лікування',
    update: 'Помилка оновлення лікування',
    delete: 'Помилка видалення лікування',
  },
})

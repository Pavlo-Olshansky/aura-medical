import type { Vaccination } from '@/types'
import { demo, demoSort } from '@/stores/demoRegistry'
import {
  listVaccinations as apiListVaccinations,
  getVaccination as apiGetVaccination,
  createVaccination as apiCreateVaccination,
  updateVaccination as apiUpdateVaccination,
  deleteVaccination as apiDeleteVaccination,
} from '@/api/vaccinations'
import { createEntityStore } from '@/stores/factory/useDataStore'

function vaccinationFromFormData(formData: FormData): Omit<Vaccination, 'id'> {
  const now = new Date().toISOString()
  const get = (k: string) => {
    const v = formData.get(k)
    return typeof v === 'string' && v.length > 0 ? v : null
  }
  const date = get('date') ?? now.slice(0, 10)
  const days = get('next_due_date')
  const today = new Date()
  const dueDate = days ? new Date(days) : null
  let status: Vaccination['status'] = 'completed'
  if (dueDate) status = dueDate < today ? 'overdue' : 'upcoming'
  return {
    date,
    vaccine_name: get('vaccine_name') ?? '',
    manufacturer: get('manufacturer'),
    lot_number: get('lot_number'),
    dose_number: Number(get('dose_number') ?? 1),
    next_due_date: days,
    notes: get('notes'),
    has_document: false,
    status,
    created: now,
    updated: now,
  }
}

export const useVaccinationsStore = createEntityStore<Vaccination, FormData, FormData>({
  id: 'vaccinations',
  api: {
    list: apiListVaccinations,
    get: apiGetVaccination,
    create: apiCreateVaccination,
    update: apiUpdateVaccination,
    delete: apiDeleteVaccination,
  },
  demo: {
    list: (params) => {
      let all = demo().getVaccinations()
      if (params?.status) all = all.filter((v) => v.status === params.status)
      if (params?.date_from) all = all.filter((v) => v.date >= (params.date_from as string))
      if (params?.date_to) all = all.filter((v) => v.date <= (params.date_to as string))
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
    get: (id) => demo().getVaccinations().find((v) => v.id === id),
    create: (formData) => demo().create(demo().getVaccinations(), vaccinationFromFormData(formData)),
    update: (id, formData) => demo().update(demo().getVaccinations(), id, vaccinationFromFormData(formData)),
    delete: (id) => demo().remove(demo().getVaccinations(), id),
  },
  errorMessages: {
    list: 'Помилка завантаження вакцинацій',
    get: 'Помилка завантаження вакцинації',
    create: 'Помилка створення вакцинації',
    update: 'Помилка оновлення вакцинації',
    delete: 'Помилка видалення вакцинації',
  },
})

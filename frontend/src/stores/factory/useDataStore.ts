import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PaginatedResponse } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'

export interface StoreApiConfig<T, TCreate = unknown, TUpdate = unknown> {
  list: (params?: Record<string, unknown>) => Promise<PaginatedResponse<T>>
  get: (id: number) => Promise<T>
  create: (data: TCreate) => Promise<T>
  update: (id: number, data: TUpdate) => Promise<T>
  delete: (id: number) => Promise<void>
}

export interface StoreDemoConfig<T, TCreate = unknown, TUpdate = unknown> {
  list: (params?: Record<string, unknown>) => PaginatedResponse<T>
  get: (id: number) => T | undefined
  create: (data: TCreate) => T
  update: (id: number, data: TUpdate) => T | undefined
  delete: (id: number) => boolean
}

export interface DataStoreConfig<T, TCreate = unknown, TUpdate = unknown> {
  id: string
  api: StoreApiConfig<T, TCreate, TUpdate>
  demo?: StoreDemoConfig<T, TCreate, TUpdate>
  errorMessages?: {
    list?: string
    get?: string
    create?: string
    update?: string
    delete?: string
  }
}

export function createEntityStore<T, TCreate = unknown, TUpdate = unknown>(
  config: DataStoreConfig<T, TCreate, TUpdate>,
) {
  return defineStore(config.id, () => {
    const items = ref<T[]>([]) as ReturnType<typeof ref<T[]>>
    const currentItem = ref<T | null>(null) as ReturnType<typeof ref<T | null>>
    const total = ref(0)
    const page = ref(1)
    const size = ref(20)
    const pages = ref(0)
    const loading = ref(false)
    const error = ref<string | null>(null)

    const msgs = config.errorMessages ?? {}

    function applyPaginated(data: PaginatedResponse<T>) {
      items.value = data.items as T[]
      total.value = data.total
      page.value = data.page
      size.value = data.size
      pages.value = data.pages
    }

    async function fetchList(params?: Record<string, unknown>) {
      if (isDemoMode.value && config.demo) {
        const data = config.demo.list(params)
        applyPaginated(data)
        return
      }
      loading.value = true
      error.value = null
      try {
        const data = await config.api.list(params)
        applyPaginated(data)
      } catch (e: unknown) {
        error.value = getErrorMessage(e, msgs.list ?? 'Помилка завантаження')
        throw e
      } finally {
        loading.value = false
      }
    }

    async function fetchOne(id: number) {
      if (isDemoMode.value && config.demo) {
        currentItem.value = (config.demo.get(id) ?? null) as T | null
        return
      }
      loading.value = true
      error.value = null
      try {
        currentItem.value = await config.api.get(id) as T
      } catch (e: unknown) {
        error.value = getErrorMessage(e, msgs.get ?? 'Помилка завантаження')
        throw e
      } finally {
        loading.value = false
      }
    }

    async function create(data: TCreate): Promise<T> {
      if (isDemoMode.value && config.demo) {
        const created = config.demo.create(data)
        return created
      }
      loading.value = true
      error.value = null
      try {
        const result = await config.api.create(data)
        return result
      } catch (e: unknown) {
        error.value = getErrorMessage(e, msgs.create ?? 'Помилка створення')
        throw e
      } finally {
        loading.value = false
      }
    }

    async function update(id: number, data: TUpdate): Promise<T> {
      if (isDemoMode.value && config.demo) {
        const updated = config.demo.update(id, data)
        if (updated) currentItem.value = updated as T
        return updated as T
      }
      loading.value = true
      error.value = null
      try {
        const result = await config.api.update(id, data)
        currentItem.value = result as T
        return result
      } catch (e: unknown) {
        error.value = getErrorMessage(e, msgs.update ?? 'Помилка оновлення')
        throw e
      } finally {
        loading.value = false
      }
    }

    async function remove(id: number) {
      if (isDemoMode.value && config.demo) {
        config.demo.delete(id)
        currentItem.value = null
        return
      }
      loading.value = true
      error.value = null
      try {
        await config.api.delete(id)
        currentItem.value = null
      } catch (e: unknown) {
        error.value = getErrorMessage(e, msgs.delete ?? 'Помилка видалення')
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
      fetchList,
      fetchOne,
      create,
      update,
      remove,
    }
  })
}

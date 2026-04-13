import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Reference } from '@/types'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import {
  listResource,
  createResource,
  updateResource,
  deleteResource,
  type ReferenceResource,
} from '@/api/references'

export const useReferencesStore = defineStore('references', () => {
  const positions = ref<Reference[]>([])
  const procedures = ref<Reference[]>([])
  const clinics = ref<Reference[]>([])
  const cities = ref<Reference[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  function getList(resource: ReferenceResource): Reference[] {
    const map: Record<ReferenceResource, Reference[]> = {
      positions: positions.value,
      procedures: procedures.value,
      clinics: clinics.value,
      cities: cities.value,
    }
    return map[resource]
  }

  function setList(resource: ReferenceResource, data: Reference[]) {
    switch (resource) {
      case 'positions':
        positions.value = data
        break
      case 'procedures':
        procedures.value = data
        break
      case 'clinics':
        clinics.value = data
        break
      case 'cities':
        cities.value = data
        break
    }
  }

  async function fetchAll() {
    if (isDemoMode.value) {
      positions.value = demo().getReferences('positions')
      procedures.value = demo().getReferences('procedures')
      clinics.value = demo().getReferences('clinics')
      cities.value = demo().getReferences('cities')
      return
    }
    loading.value = true
    error.value = null
    try {
      const [pos, proc, clin, cit] = await Promise.all([
        listResource('positions', undefined, 'recent'),
        listResource('procedures', undefined, 'recent'),
        listResource('clinics', undefined, 'recent'),
        listResource('cities', undefined, 'recent'),
      ])
      positions.value = pos
      procedures.value = proc
      clinics.value = clin
      cities.value = cit
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження довідників')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchResource(resource: ReferenceResource, search?: string) {
    if (isDemoMode.value) {
      let items = demo().getReferences(resource)
      if (search) {
        const q = search.toLowerCase()
        items = items.filter((r) => r.name.toLowerCase().includes(q))
      }
      setList(resource, items)
      return
    }
    loading.value = true
    error.value = null
    try {
      const data = await listResource(resource, search)
      setList(resource, data)
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка завантаження довідника')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function addResource(resource: ReferenceResource, name: string) {
    if (isDemoMode.value) {
      const now = new Date().toISOString()
      const created = demo().create(demo().getReferences(resource), {
        name,
        created: now,
        updated: now,
      })
      setList(resource, [...demo().getReferences(resource)])
      return created
    }
    loading.value = true
    error.value = null
    try {
      const item = await createResource(resource, name)
      const list = getList(resource)
      setList(resource, [...list, item])
      return item
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка створення запису')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function editResource(resource: ReferenceResource, id: number, name: string) {
    if (isDemoMode.value) {
      const updated = demo().update(demo().getReferences(resource), id, {
        name,
        updated: new Date().toISOString(),
      })
      setList(resource, [...demo().getReferences(resource)])
      return updated as Reference
    }
    loading.value = true
    error.value = null
    try {
      const updated = await updateResource(resource, id, name)
      const list = getList(resource)
      setList(
        resource,
        list.map((item) => (item.id === id ? updated : item)),
      )
      return updated
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка оновлення запису')
      throw e
    } finally {
      loading.value = false
    }
  }

  async function removeResource(resource: ReferenceResource, id: number) {
    if (isDemoMode.value) {
      demo().remove(demo().getReferences(resource), id)
      setList(resource, [...demo().getReferences(resource)])
      return
    }
    loading.value = true
    error.value = null
    try {
      await deleteResource(resource, id)
      const list = getList(resource)
      setList(
        resource,
        list.filter((item) => item.id !== id),
      )
    } catch (e: unknown) {
      error.value = getErrorMessage(e, 'Помилка видалення запису')
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    positions,
    procedures,
    clinics,
    cities,
    loading,
    error,
    getList,
    fetchAll,
    fetchResource,
    addResource,
    editResource,
    removeResource,
  }
})

import { ref, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export type FilterType = 'number' | 'string' | 'date'

export interface FilterDef {
  name: string
  type: FilterType
  default: unknown
}

type FilterValue<T extends FilterType> = T extends 'number'
  ? number | null
  : T extends 'date'
    ? Date | null
    : string | null

type FilterRefs<T extends readonly FilterDef[]> = {
  [K in T[number]['name']]: Ref<FilterValue<Extract<T[number], { name: K }>['type']>>
}

function parseQueryValue(value: string | undefined | null, type: FilterType, defaultVal: unknown): unknown {
  if (value == null || value === '') return defaultVal
  switch (type) {
    case 'number': {
      const n = parseInt(value, 10)
      return isNaN(n) ? defaultVal : n
    }
    case 'date': {
      const d = new Date(value)
      return isNaN(d.getTime()) ? defaultVal : d
    }
    case 'string':
      return value
  }
}

function toQueryString(value: unknown, type: FilterType): string | undefined {
  if (value == null) return undefined
  switch (type) {
    case 'number':
      return String(value)
    case 'date': {
      const d = value as Date
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
    case 'string':
      return value as string
  }
}

export function useUrlFilters<T extends readonly FilterDef[]>(
  filters: T,
): FilterRefs<T> & { syncToUrl: () => void; clearAll: () => void } {
  const route = useRoute()
  const router = useRouter()

  const refs: Record<string, Ref> = {}

  for (const filter of filters) {
    const queryVal = route.query[filter.name] as string | undefined
    const initial = parseQueryValue(queryVal, filter.type, filter.default)
    refs[filter.name] = ref(initial)
  }

  function syncToUrl() {
    const query: Record<string, string> = {}
    for (const filter of filters) {
      const val = refs[filter.name]!.value
      if (val != null && val !== filter.default) {
        const str = toQueryString(val, filter.type)
        if (str != null) query[filter.name] = str
      }
    }
    router.replace({ query })
  }

  function clearAll() {
    for (const filter of filters) {
      refs[filter.name]!.value = filter.default as any
    }
    router.replace({ query: {} })
  }

  return { ...refs, syncToUrl, clearAll } as FilterRefs<T> & { syncToUrl: () => void; clearAll: () => void }
}

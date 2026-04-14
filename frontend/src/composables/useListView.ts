import { ref, watch, onMounted, type Ref } from 'vue'
import { useUrlFilters, type FilterDef } from '@/composables/useUrlFilters'

export interface ListViewConfig<T extends readonly FilterDef[]> {
  fetchList: (params: Record<string, unknown>) => Promise<void>
  filters: T
  defaultSize?: number
  defaultSort?: string
  buildParams?: (
    filters: Record<string, unknown>,
    page: number,
    size: number,
    sort: string,
  ) => Record<string, unknown>
}

export function useListView<T extends readonly FilterDef[]>(config: ListViewConfig<T>) {
  const filterResult = useUrlFilters(config.filters)
  const { syncToUrl, clearAll: clearFilters, ...filterRefs } = filterResult

  const page = ref((filterRefs as Record<string, Ref>).page?.value ?? 1) as Ref<number>
  const size = ref(
    (filterRefs as Record<string, Ref>).size?.value ?? config.defaultSize ?? 20,
  ) as Ref<number>
  const sort = ref(
    (filterRefs as Record<string, Ref>).sort?.value ?? config.defaultSort ?? '-date',
  ) as Ref<string>
  const loading = ref(false)

  function getFilterValues(): Record<string, unknown> {
    const result: Record<string, unknown> = {}
    for (const f of config.filters) {
      if (f.name === 'page' || f.name === 'size' || f.name === 'sort') continue
      const val = (filterRefs as Record<string, Ref>)[f.name]?.value
      if (val != null && val !== f.default) {
        result[f.name] = val
      }
    }
    return result
  }

  function buildRequestParams(): Record<string, unknown> {
    const filterValues = getFilterValues()
    if (config.buildParams) {
      return config.buildParams(filterValues, page.value, size.value, sort.value)
    }
    return {
      ...filterValues,
      page: page.value,
      size: size.value,
      sort: sort.value,
    }
  }

  async function loadData() {
    loading.value = true
    try {
      await config.fetchList(buildRequestParams())
    } finally {
      loading.value = false
    }
    // Sync current page/size/sort back to URL filters
    const refs = filterRefs as Record<string, Ref>
    if (refs.page) refs.page.value = page.value
    if (refs.size) refs.size.value = size.value
    if (refs.sort) refs.sort.value = sort.value
    syncToUrl()
  }

  function onPage(event: { page: number; rows: number }) {
    page.value = event.page + 1
    size.value = event.rows
    loadData()
  }

  function onSort(event: { sortField: string; sortOrder: number }) {
    if (event.sortField) {
      sort.value = (event.sortOrder === -1 ? '-' : '') + event.sortField
    }
    page.value = 1
    loadData()
  }

  function resetFilters() {
    clearFilters()
    page.value = 1
    size.value = config.defaultSize ?? 20
    sort.value = config.defaultSort ?? '-date'
    loadData()
  }

  // Watch non-pagination filters for changes
  const filterWatchSources = config.filters
    .filter((f) => f.name !== 'page' && f.name !== 'size' && f.name !== 'sort')
    .map((f) => () => (filterRefs as Record<string, Ref>)[f.name]?.value)

  if (filterWatchSources.length > 0) {
    watch(filterWatchSources, () => {
      page.value = 1
      loadData()
    })
  }

  onMounted(() => {
    loadData()
  })

  return {
    filters: filterRefs,
    page,
    size,
    sort,
    loading,
    loadData,
    onPage,
    onSort,
    clearFilters: resetFilters,
    syncToUrl,
  }
}

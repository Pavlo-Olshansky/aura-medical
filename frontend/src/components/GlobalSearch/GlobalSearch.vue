<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import { globalSearch } from '@/api/search'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import GlobalSearchInput from './GlobalSearchInput.vue'
import GlobalSearchResults from './GlobalSearchResults.vue'
import type {
  SearchResponse,
  VisitSearchItem,
  TreatmentSearchItem,
  LabResultSearchItem,
  VaccinationSearchItem,
} from '@/types'

function demoSearch(q: string): SearchResponse {
  const needle = q.toLowerCase()
  const visits: VisitSearchItem[] = demo()
    .getVisits()
    .filter((v) =>
      [v.doctor, v.position?.name, v.procedure?.name, v.clinic?.name, v.city?.name, v.body_region, v.comment]
        .filter(Boolean)
        .some((field) => String(field).toLowerCase().includes(needle)),
    )
    .map((v) => ({
      id: v.id,
      date: v.date,
      doctor: v.doctor,
      position_name: v.position?.name ?? null,
      procedure_name: v.procedure?.name ?? null,
      clinic_name: v.clinic?.name ?? null,
      city_name: v.city?.name ?? null,
      body_region: v.body_region,
      comment: v.comment,
    }))
  const treatments: TreatmentSearchItem[] = demo()
    .getTreatments()
    .filter((t) => t.name.toLowerCase().includes(needle))
    .map((t) => ({
      id: t.id,
      date_start: t.date_start,
      name: t.name,
      days: t.days,
      status: t.status,
      body_region: t.body_region,
    }))
  const labResults: LabResultSearchItem[] = demo()
    .getLabResults()
    .filter((r) =>
      (r.notes?.toLowerCase().includes(needle) ?? false) ||
      r.entries.some((e) => e.biomarker_name.toLowerCase().includes(needle)),
    )
    .map((r) => ({
      id: r.id,
      date: r.date,
      notes: r.notes,
      entries_count: r.entries.length,
      biomarker_names: r.entries.map((e) => e.biomarker_name),
      visit_id: r.visit_id,
    }))
  const vaccinations: VaccinationSearchItem[] = demo()
    .getVaccinations()
    .filter(
      (v) =>
        v.vaccine_name.toLowerCase().includes(needle) ||
        (v.manufacturer?.toLowerCase().includes(needle) ?? false),
    )
    .map((v) => ({
      id: v.id,
      date: v.date,
      vaccine_name: v.vaccine_name,
      dose_number: v.dose_number,
      manufacturer: v.manufacturer,
      notes: v.notes,
    }))
  return {
    visits: { items: visits, total: visits.length },
    treatments: { items: treatments, total: treatments.length },
    lab_results: { items: labResults, total: labResults.length },
    vaccinations: { items: vaccinations, total: vaccinations.length },
  }
}

const visible = defineModel<boolean>('visible', { required: true })
const router = useRouter()

const query = ref('')
const results = ref<SearchResponse | null>(null)
const loading = ref(false)
const error = ref(false)
const activeIndex = ref(-1)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

interface FlatItem {
  type: 'visit' | 'treatment' | 'lab_result' | 'vaccination'
  id: number
}

const flatItems = computed<FlatItem[]>(() => {
  if (!results.value) return []
  const items: FlatItem[] = []
  for (const v of results.value.visits.items) items.push({ type: 'visit', id: v.id })
  for (const t of results.value.treatments.items) items.push({ type: 'treatment', id: t.id })
  for (const l of results.value.lab_results.items) items.push({ type: 'lab_result', id: l.id })
  for (const v of results.value.vaccinations.items) items.push({ type: 'vaccination', id: v.id })
  return items
})

watch(query, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  activeIndex.value = -1
  if (val.trim().length < 2) {
    results.value = null
    loading.value = false
    error.value = false
    return
  }
  loading.value = true
  error.value = false
  debounceTimer = setTimeout(async () => {
    try {
      results.value = isDemoMode.value
        ? demoSearch(val.trim())
        : await globalSearch(val.trim())
      error.value = false
    } catch {
      error.value = true
      results.value = null
    } finally {
      loading.value = false
    }
  }, 300)
})

function navigateTo(type: string, id: number) {
  const routes: Record<string, string> = {
    visit: `/visits/${id}`,
    treatment: `/treatments/${id}/edit`,
    lab_result: `/lab-results/${id}`,
    vaccination: `/vaccinations/${id}/edit`,
  }
  const route = routes[type]
  if (route) router.push(route)
  closeDialog()
}

function closeDialog() {
  visible.value = false
}

function resetState() {
  query.value = ''
  results.value = null
  loading.value = false
  error.value = false
  activeIndex.value = -1
  if (debounceTimer) clearTimeout(debounceTimer)
}

function onShow() {
  nextTick(() => {
    const input = document.querySelector('.global-search-input input') as HTMLInputElement
    input?.focus()
  })
}

function onHide() {
  resetState()
}

function onKeydown(e: KeyboardEvent) {
  const total = flatItems.value.length
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (total > 0) {
      activeIndex.value = Math.min(activeIndex.value + 1, total - 1)
      scrollToActive()
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, -1)
    if (activeIndex.value === -1) {
      const input = document.querySelector('.global-search-input input') as HTMLInputElement
      input?.focus()
    } else {
      scrollToActive()
    }
  } else if (e.key === 'Enter' && activeIndex.value >= 0) {
    e.preventDefault()
    const item = flatItems.value[activeIndex.value]
    if (item) navigateTo(item.type, item.id)
  }
}

function scrollToActive() {
  nextTick(() => {
    const el = document.querySelector('.search-result-item.active')
    el?.scrollIntoView({ block: 'nearest' })
  })
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    position="top"
    :style="{ width: 'min(860px, 92vw)' }"
    :pt="{
      root: { class: 'global-search-dialog' },
      content: { class: 'global-search-content' },
    }"
    @show="onShow"
    @hide="onHide"
    @keydown="onKeydown"
  >
    <template #header>
      <GlobalSearchInput v-model:query="query" @close="closeDialog" />
    </template>

    <GlobalSearchResults
      :query="query"
      :results="results"
      :loading="loading"
      :error="error"
      :active-index="activeIndex"
      @navigate="navigateTo"
      @update:active-index="activeIndex = $event"
      @close="closeDialog"
    />
  </Dialog>
</template>

<style scoped>
:deep(.global-search-dialog) {
  margin-top: 8vh;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 16px 70px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 0, 0, 0.08);
}

:deep(.global-search-dialog .p-dialog-header) {
  padding: 0;
  border-bottom: 1px solid var(--border-subtle);
}

:deep(.global-search-content) {
  padding: 0;
  max-height: 60vh;
  overflow-y: auto;
}
</style>

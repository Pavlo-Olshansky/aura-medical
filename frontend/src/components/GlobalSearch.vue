<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import ProgressSpinner from 'primevue/progressspinner'
import { globalSearch } from '@/api/search'
import type {
  SearchResponse,
  VisitSearchItem,
  TreatmentSearchItem,
  LabResultSearchItem,
  VaccinationSearchItem,
} from '@/types'

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

const hasResults = computed(() => {
  if (!results.value) return false
  return (
    results.value.visits.total > 0 ||
    results.value.treatments.total > 0 ||
    results.value.lab_results.total > 0 ||
    results.value.vaccinations.total > 0
  )
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
      results.value = await globalSearch(val.trim())
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

function getItemGlobalIndex(type: string, localIndex: number): number {
  if (!results.value) return -1
  let offset = 0
  if (type === 'visit') return localIndex
  offset += results.value.visits.items.length
  if (type === 'treatment') return offset + localIndex
  offset += results.value.treatments.items.length
  if (type === 'lab_result') return offset + localIndex
  offset += results.value.lab_results.items.length
  if (type === 'vaccination') return offset + localIndex
  return -1
}

function highlight(text: string | null): string {
  if (!text || !query.value || query.value.trim().length < 2) return text || ''
  const escaped = query.value.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'giu')
  const safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return safe.replace(regex, '<mark>$1</mark>')
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="false"
    position="top"
    :pt="{
      root: { class: 'global-search-dialog' },
      content: { class: 'global-search-content' },
    }"
    @show="onShow"
    @hide="onHide"
    @keydown="onKeydown"
  >
    <template #header>
      <div class="global-search-header">
        <i class="pi pi-search search-icon" />
        <InputText
          v-model="query"
          class="global-search-input"
          placeholder="Пошук по візитам, лікуванням, аналізам, вакцинаціям..."
          autofocus
        />
        <kbd class="search-kbd" @click="closeDialog">Esc</kbd>
      </div>
    </template>

    <div class="search-body">
      <!-- Min length hint -->
      <div v-if="query.trim().length > 0 && query.trim().length < 2" class="search-hint">
        Введіть мінімум 2 символи
      </div>

      <!-- Loading -->
      <div v-else-if="loading" class="search-loading">
        <ProgressSpinner style="width: 24px; height: 24px" strokeWidth="4" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="search-error">
        Помилка пошуку. Спробуйте ще раз.
      </div>

      <!-- No results -->
      <div v-else-if="results && !hasResults" class="search-empty">
        Нічого не знайдено
      </div>

      <!-- Results -->
      <div v-else-if="results && hasResults" class="search-results">
        <!-- Visits -->
        <div v-if="results.visits.items.length > 0" class="search-group">
          <div class="search-group-header">
            <i class="pi pi-calendar" />
            <span>Візити</span>
            <span class="search-group-count">{{ results.visits.total }}</span>
          </div>
          <div
            v-for="(item, idx) in results.visits.items"
            :key="'v-' + item.id"
            class="search-result-item"
            :class="{ active: activeIndex === getItemGlobalIndex('visit', idx) }"
            @click="navigateTo('visit', item.id)"
            @mouseenter="activeIndex = getItemGlobalIndex('visit', idx)"
          >
            <div class="result-main" v-html="highlight(item.doctor || item.procedure_name || item.comment || '—')" />
            <div class="result-details">
              <span class="result-date">{{ formatDate(item.date) }}</span>
              <span v-if="item.position_name" class="result-tag">{{ item.position_name }}</span>
              <span v-if="item.clinic_name" class="result-tag">{{ item.clinic_name }}</span>
            </div>
          </div>
          <RouterLink
            v-if="results.visits.total > results.visits.items.length"
            :to="{ path: '/visits', query: { search: query } }"
            class="search-show-all"
            @click="closeDialog"
          >
            Показати всі ({{ results.visits.total }})
          </RouterLink>
        </div>

        <!-- Treatments -->
        <div v-if="results.treatments.items.length > 0" class="search-group">
          <div class="search-group-header">
            <i class="pi pi-heart" />
            <span>Лікування</span>
            <span class="search-group-count">{{ results.treatments.total }}</span>
          </div>
          <div
            v-for="(item, idx) in results.treatments.items"
            :key="'t-' + item.id"
            class="search-result-item"
            :class="{ active: activeIndex === getItemGlobalIndex('treatment', idx) }"
            @click="navigateTo('treatment', item.id)"
            @mouseenter="activeIndex = getItemGlobalIndex('treatment', idx)"
          >
            <div class="result-main" v-html="highlight(item.name)" />
            <div class="result-details">
              <span class="result-date">{{ formatDate(item.date_start) }}</span>
              <span class="result-status" :class="item.status">
                {{ item.status === 'active' ? 'Активне' : 'Завершено' }}
              </span>
            </div>
          </div>
          <RouterLink
            v-if="results.treatments.total > results.treatments.items.length"
            :to="{ path: '/treatments', query: { search: query } }"
            class="search-show-all"
            @click="closeDialog"
          >
            Показати всі ({{ results.treatments.total }})
          </RouterLink>
        </div>

        <!-- Lab Results -->
        <div v-if="results.lab_results.items.length > 0" class="search-group">
          <div class="search-group-header">
            <i class="pi pi-chart-bar" />
            <span>Аналізи</span>
            <span class="search-group-count">{{ results.lab_results.total }}</span>
          </div>
          <div
            v-for="(item, idx) in results.lab_results.items"
            :key="'l-' + item.id"
            class="search-result-item"
            :class="{ active: activeIndex === getItemGlobalIndex('lab_result', idx) }"
            @click="navigateTo('lab_result', item.id)"
            @mouseenter="activeIndex = getItemGlobalIndex('lab_result', idx)"
          >
            <div class="result-main" v-html="highlight(item.biomarker_names.join(', ') || item.notes || '—')" />
            <div class="result-details">
              <span class="result-date">{{ formatDate(item.date) }}</span>
              <span v-if="item.notes" class="result-tag" v-html="highlight(item.notes)" />
            </div>
          </div>
          <RouterLink
            v-if="results.lab_results.total > results.lab_results.items.length"
            :to="{ path: '/lab-results', query: { search: query } }"
            class="search-show-all"
            @click="closeDialog"
          >
            Показати всі ({{ results.lab_results.total }})
          </RouterLink>
        </div>

        <!-- Vaccinations -->
        <div v-if="results.vaccinations.items.length > 0" class="search-group">
          <div class="search-group-header">
            <i class="pi pi-shield" />
            <span>Вакцинації</span>
            <span class="search-group-count">{{ results.vaccinations.total }}</span>
          </div>
          <div
            v-for="(item, idx) in results.vaccinations.items"
            :key="'vac-' + item.id"
            class="search-result-item"
            :class="{ active: activeIndex === getItemGlobalIndex('vaccination', idx) }"
            @click="navigateTo('vaccination', item.id)"
            @mouseenter="activeIndex = getItemGlobalIndex('vaccination', idx)"
          >
            <div class="result-main" v-html="highlight(item.vaccine_name)" />
            <div class="result-details">
              <span class="result-date">{{ formatDate(item.date) }}</span>
              <span class="result-tag">Доза {{ item.dose_number }}</span>
              <span v-if="item.manufacturer" class="result-tag" v-html="highlight(item.manufacturer)" />
            </div>
          </div>
          <RouterLink
            v-if="results.vaccinations.total > results.vaccinations.items.length"
            :to="{ path: '/vaccinations', query: { search: query } }"
            class="search-show-all"
            @click="closeDialog"
          >
            Показати всі ({{ results.vaccinations.total }})
          </RouterLink>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
:deep(.global-search-dialog) {
  width: min(680px, 92vw);
  margin-top: 10vh;
  border-radius: 12px;
  overflow: hidden;
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

.global-search-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  width: 100%;
}

.search-icon {
  color: var(--text-muted);
  font-size: 1.25rem;
  flex-shrink: 0;
}

:deep(.global-search-input) {
  flex: 1;
  min-width: 0;
  border: none;
  box-shadow: none;
  font-size: 1.125rem;
  padding: 0.5rem 0;
  background: transparent;
  color: var(--text-primary);
}

:deep(.global-search-input:focus) {
  box-shadow: none;
  outline: none;
}

.search-kbd {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  background: var(--bg-hover);
}

.search-body {
  padding: 0.5rem 0;
}

.search-hint,
.search-empty,
.search-error {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.search-error {
  color: var(--danger);
}

.search-loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.search-group {
  padding: 0.25rem 0;
}

.search-group + .search-group {
  border-top: 1px solid var(--border-subtle);
}

.search-group-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.search-group-count {
  margin-left: auto;
  font-size: 0.7rem;
  background: var(--bg-hover);
  padding: 0.1rem 0.4rem;
  border-radius: 8px;
}

.search-result-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background 0.1s;
}

.search-result-item:hover,
.search-result-item.active {
  background: var(--bg-hover);
}

.result-main {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 0.15rem;
}

.result-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.result-date {
  font-variant-numeric: tabular-nums;
}

.result-tag {
  background: var(--bg-hover);
  padding: 0.05rem 0.4rem;
  border-radius: 4px;
}

.result-status {
  padding: 0.05rem 0.4rem;
  border-radius: 4px;
  font-weight: 500;
}

.result-status.active {
  background: rgba(34, 197, 94, 0.15);
  color: rgb(34, 197, 94);
}

.result-status.completed {
  background: var(--bg-hover);
  color: var(--text-muted);
}

.search-show-all {
  display: block;
  text-align: center;
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: none;
  cursor: pointer;
}

.search-show-all:hover {
  text-decoration: underline;
}

:deep(mark) {
  background: rgba(250, 204, 21, 0.3);
  color: inherit;
  padding: 0;
  border-radius: 2px;
}

.dark :deep(mark) {
  background: rgba(250, 204, 21, 0.2);
}
</style>

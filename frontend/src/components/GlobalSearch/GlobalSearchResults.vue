<script setup lang="ts">
import { computed } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import type { SearchResponse } from '@/types'

const props = defineProps<{
  query: string
  results: SearchResponse | null
  loading: boolean
  error: boolean
  activeIndex: number
}>()

const emit = defineEmits<{
  navigate: [type: string, id: number]
  'update:activeIndex': [value: number]
  close: []
}>()

function getItemGlobalIndex(type: string, localIndex: number): number {
  if (!props.results) return -1
  let offset = 0
  if (type === 'visit') return localIndex
  offset += props.results.visits.items.length
  if (type === 'treatment') return offset + localIndex
  offset += props.results.treatments.items.length
  if (type === 'lab_result') return offset + localIndex
  offset += props.results.lab_results.items.length
  if (type === 'vaccination') return offset + localIndex
  return -1
}

function highlight(text: string | null): string {
  if (!text || !props.query || props.query.trim().length < 2) return text || ''
  const escaped = props.query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'giu')
  const safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  return safe.replace(regex, '<mark>$1</mark>')
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const hasResults = computed(() => {
  if (!props.results) return false
  return (
    props.results.visits.total > 0 ||
    props.results.treatments.total > 0 ||
    props.results.lab_results.total > 0 ||
    props.results.vaccinations.total > 0
  )
})
</script>

<template>
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
          @click="emit('navigate', 'visit', item.id)"
          @mouseenter="emit('update:activeIndex', getItemGlobalIndex('visit', idx))"
        >
          <div class="result-main" v-html="highlight(item.doctor || item.procedure_name || '—')" />
          <div class="result-details">
            <span class="result-date">{{ formatDate(item.date) }}</span>
            <span v-if="item.position_name" class="result-tag">{{ item.position_name }}</span>
            <span v-if="item.clinic_name" class="result-tag">{{ item.clinic_name }}</span>
          </div>
          <div v-if="item.comment" class="result-comment" v-html="highlight(item.comment)" />
        </div>
        <RouterLink
          v-if="results.visits.total > results.visits.items.length"
          :to="{ path: '/visits', query: { search: query } }"
          class="search-show-all"
          @click="emit('close')"
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
          @click="emit('navigate', 'treatment', item.id)"
          @mouseenter="emit('update:activeIndex', getItemGlobalIndex('treatment', idx))"
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
          @click="emit('close')"
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
          @click="emit('navigate', 'lab_result', item.id)"
          @mouseenter="emit('update:activeIndex', getItemGlobalIndex('lab_result', idx))"
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
          @click="emit('close')"
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
          @click="emit('navigate', 'vaccination', item.id)"
          @mouseenter="emit('update:activeIndex', getItemGlobalIndex('vaccination', idx))"
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
          @click="emit('close')"
        >
          Показати всі ({{ results.vaccinations.total }})
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
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

.result-comment {
  font-size: 0.75rem;
  color: var(--text-faint);
  margin-top: 0.15rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

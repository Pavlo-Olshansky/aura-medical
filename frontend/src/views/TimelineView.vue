<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Tag from 'primevue/tag'
import { useTimelineStore } from '@/stores/timeline'
import type { TimelineEvent } from '@/types'

const router = useRouter()
const timelineStore = useTimelineStore()

const currentPage = ref(1)
const pageSize = ref(20)

const eventTypeFilter = ref<string | null>(null)
const dateFrom = ref<Date | null>(null)
const dateTo = ref<Date | null>(null)

const eventTypeOptions = [
  { label: 'Візити', value: 'visit' },
  { label: 'Лікування', value: 'treatment' },
  { label: 'Аналізи', value: 'lab_result' },
  { label: 'Вакцинації', value: 'vaccination' },
]

const eventTypeConfig: Record<string, { label: string; severity: string; icon: string }> = {
  visit: { label: 'Візит', severity: 'info', icon: 'pi pi-calendar' },
  treatment: { label: 'Лікування', severity: 'success', icon: 'pi pi-heart' },
  lab_result: { label: 'Аналіз', severity: 'help', icon: 'pi pi-chart-bar' },
  vaccination: { label: 'Вакцинація', severity: 'warn', icon: 'pi pi-shield' },
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatDateParam(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function loadTimeline() {
  const params: Record<string, any> = {
    page: currentPage.value,
    size: pageSize.value,
  }
  if (eventTypeFilter.value) params.event_type = eventTypeFilter.value
  if (dateFrom.value) params.date_from = formatDateParam(dateFrom.value)
  if (dateTo.value) params.date_to = formatDateParam(dateTo.value)

  await timelineStore.fetchTimeline(params)
}

function navigateToEvent(event: TimelineEvent) {
  router.push(event.route)
}

function clearFilters() {
  eventTypeFilter.value = null
  dateFrom.value = null
  dateTo.value = null
  currentPage.value = 1
  loadTimeline()
}

const totalPages = computed(() => Math.ceil(timelineStore.total / pageSize.value))

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    loadTimeline()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadTimeline()
  }
}

watch([eventTypeFilter, dateFrom, dateTo], () => {
  currentPage.value = 1
  loadTimeline()
})

onMounted(() => {
  loadTimeline()
})
</script>

<template>
  <div class="timeline-view">
    <div class="page-header">
      <h1>Хронологія</h1>
    </div>

    <div class="filters">
      <div class="filter-row">
        <div class="filter-item">
          <label>Тип події</label>
          <Dropdown
            v-model="eventTypeFilter"
            :options="eventTypeOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Всі типи"
            showClear
          />
        </div>
        <div class="filter-item">
          <label>Дата від</label>
          <Calendar v-model="dateFrom" dateFormat="dd.mm.yy" placeholder="Дата від" showIcon />
        </div>
        <div class="filter-item">
          <label>Дата до</label>
          <Calendar v-model="dateTo" dateFormat="dd.mm.yy" placeholder="Дата до" showIcon />
        </div>
        <div class="filter-item filter-actions">
          <Button label="Очистити" icon="pi pi-filter-slash" severity="secondary" text @click="clearFilters" />
        </div>
      </div>
    </div>

    <div v-if="timelineStore.loading" class="loading">Завантаження...</div>

    <div v-else-if="timelineStore.events.length === 0" class="empty-state">
      Подій не знайдено
    </div>

    <div v-else class="timeline-list">
      <div
        v-for="event in timelineStore.events"
        :key="`${event.event_type}-${event.event_id}`"
        class="timeline-card"
        @click="navigateToEvent(event)"
      >
        <div class="card-left">
          <div class="event-date">{{ formatDate(event.date) }}</div>
          <div class="event-icon">
            <i :class="eventTypeConfig[event.event_type]?.icon" />
          </div>
        </div>
        <div class="card-body">
          <div class="card-top">
            <Tag
              :value="eventTypeConfig[event.event_type]?.label || event.event_type"
              :severity="(eventTypeConfig[event.event_type]?.severity as any) || 'secondary'"
            />
          </div>
          <div class="event-title">{{ event.title }}</div>
          <div v-if="event.subtitle" class="event-subtitle">{{ event.subtitle }}</div>
        </div>
        <div class="card-arrow">
          <i class="pi pi-chevron-right" />
        </div>
      </div>
    </div>

    <div v-if="timelineStore.total > pageSize" class="pagination">
      <Button
        icon="pi pi-chevron-left"
        severity="secondary"
        text
        :disabled="currentPage <= 1"
        @click="prevPage"
      />
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <Button
        icon="pi pi-chevron-right"
        severity="secondary"
        text
        :disabled="currentPage >= totalPages"
        @click="nextPage"
      />
    </div>
  </div>
</template>

<style scoped>
.timeline-view {
  max-width: 900px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e4e4e7;
  margin: 0;
}
.filters {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}
.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.filter-item label {
  font-size: 0.8rem;
  color: #a1a1aa;
  font-weight: 500;
}
.filter-actions {
  justify-content: flex-end;
}
.loading {
  text-align: center;
  padding: 3rem;
  color: #52525b;
}
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #52525b;
  font-size: 0.95rem;
}
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.timeline-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.timeline-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.1);
}
.card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  min-width: 100px;
}
.event-date {
  font-size: 0.8rem;
  color: #a1a1aa;
  font-weight: 500;
  white-space: nowrap;
}
.event-icon {
  font-size: 1.125rem;
  color: #52525b;
}
.card-body {
  flex: 1;
  min-width: 0;
}
.card-top {
  margin-bottom: 0.375rem;
}
.event-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #e4e4e7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.event-subtitle {
  font-size: 0.8rem;
  color: #71717a;
  margin-top: 0.125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-arrow {
  color: #3f3f46;
  font-size: 0.875rem;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
}
.page-info {
  font-size: 0.875rem;
  color: #a1a1aa;
}
</style>

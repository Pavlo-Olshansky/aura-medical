<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import type { DataTablePageEvent, DataTableSortEvent } from 'primevue/datatable'
import { useVisitsStore } from '@/stores/visits'
import { useReferencesStore } from '@/stores/references'
import type { Visit } from '@/types'
import { formatDate } from '@/utils/dateUtils'
import { useUrlFilters } from '@/composables/useUrlFilters'

const router = useRouter()
const visitsStore = useVisitsStore()
const referencesStore = useReferencesStore()

const filterDefs = [
  { name: 'date_from', type: 'date', default: null },
  { name: 'date_to', type: 'date', default: null },
  { name: 'clinic_id', type: 'number', default: null },
  { name: 'city_id', type: 'number', default: null },
  { name: 'procedure_id', type: 'number', default: null },
  { name: 'position_id', type: 'number', default: null },
  { name: 'page', type: 'number', default: 1 },
  { name: 'size', type: 'number', default: 20 },
  { name: 'sort_order', type: 'string', default: 'desc' },
] as const

const filters = useUrlFilters(filterDefs)

function formatDateParam(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function loadVisits() {
  const params: Record<string, any> = {
    page: filters.page.value,
    size: filters.size.value,
    sort_by: 'date',
    sort_order: filters.sort_order.value,
  }
  if (filters.date_from.value) params.date_from = formatDateParam(filters.date_from.value)
  if (filters.date_to.value) params.date_to = formatDateParam(filters.date_to.value)
  if (filters.clinic_id.value) params.clinic_id = filters.clinic_id.value
  if (filters.city_id.value) params.city_id = filters.city_id.value
  if (filters.procedure_id.value) params.procedure_id = filters.procedure_id.value
  if (filters.position_id.value) params.position_id = filters.position_id.value

  await visitsStore.fetchList(params)
}

function onPage(event: DataTablePageEvent) {
  filters.page.value = event.page + 1
  filters.size.value = event.rows
  filters.syncToUrl()
  loadVisits()
}

function onSort(event: DataTableSortEvent) {
  filters.sort_order.value = event.sortOrder === 1 ? 'asc' : 'desc'
  filters.syncToUrl()
  loadVisits()
}

function onRowClick(event: { data: Visit }) {
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

function clearFilters() {
  filters.clearAll()
  loadVisits()
}

watch(
  [filters.date_from, filters.date_to, filters.clinic_id, filters.city_id, filters.procedure_id, filters.position_id],
  () => {
    filters.page.value = 1
    filters.syncToUrl()
    loadVisits()
  },
)

onMounted(async () => {
  await referencesStore.fetchAll()
  await loadVisits()
})
</script>

<template>
  <div class="visits-list">
    <div class="page-header">
      <h1>Візити</h1>
      <Button label="Новий візит" icon="pi pi-plus" @click="router.push({ name: 'visit-create' })" />
    </div>

    <div class="filters">
      <div class="filter-row">
        <div class="filter-item">
          <label>Дата від</label>
          <Calendar v-model="filters.date_from.value" dateFormat="dd.mm.yy" placeholder="Дата від" showIcon />
        </div>
        <div class="filter-item">
          <label>Дата до</label>
          <Calendar v-model="filters.date_to.value" dateFormat="dd.mm.yy" placeholder="Дата до" showIcon />
        </div>
        <div class="filter-item">
          <label>Клініка</label>
          <Dropdown
            v-model="filters.clinic_id.value"
            :options="referencesStore.clinics"
            optionLabel="name"
            optionValue="id"
            placeholder="Всі клініки"
            showClear
          />
        </div>
        <div class="filter-item">
          <label>Місто</label>
          <Dropdown
            v-model="filters.city_id.value"
            :options="referencesStore.cities"
            optionLabel="name"
            optionValue="id"
            placeholder="Всі міста"
            showClear
          />
        </div>
        <div class="filter-item">
          <label>Процедура</label>
          <Dropdown
            v-model="filters.procedure_id.value"
            :options="referencesStore.procedures"
            optionLabel="name"
            optionValue="id"
            placeholder="Всі процедури"
            showClear
          />
        </div>
        <div class="filter-item">
          <label>Позиція</label>
          <Dropdown
            v-model="filters.position_id.value"
            :options="referencesStore.positions"
            optionLabel="name"
            optionValue="id"
            placeholder="Всі позиції"
            showClear
          />
        </div>
        <div class="filter-item filter-actions">
          <Button label="Очистити" icon="pi pi-filter-slash" severity="secondary" text @click="clearFilters" />
        </div>
      </div>
    </div>

    <DataTable
      :value="visitsStore.items"
      :loading="visitsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="filters.size.value ?? 20"
      :totalRecords="visitsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      :sortField="'date'"
      :sortOrder="filters.sort_order.value === 'asc' ? 1 : -1"
      @page="onPage"
      @sort="onSort"
      @row-click="onRowClick"
      rowHover
      stripedRows
      scrollable
      class="visits-table"
    >
      <template #empty>Візитів не знайдено</template>
      <Column field="date" header="Дата" sortable>
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column header="Лікар">
        <template #body="{ data }">
          <span v-if="data.position">{{ data.position.name }}</span>
          <span v-if="data.position && data.doctor"> - </span>
          <span v-if="data.doctor">{{ data.doctor }}</span>
        </template>
      </Column>
      <Column header="Процедура">
        <template #body="{ data }">{{ data.procedure?.name || '-' }}</template>
      </Column>
      <Column header="Клініка" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">{{ data.clinic?.name || '-' }}</template>
      </Column>
      <Column header="Місто" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">{{ data.city?.name || '-' }}</template>
      </Column>
      <Column header="Документ" style="width: 80px; text-align: center" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">
          <i v-if="data.document || data.has_document" class="pi pi-file" style="color: #2563eb" />
          <span v-else>-</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.visits-list {
  max-width: 1200px;
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
  color: var(--text-primary);
  margin: 0;
}
.filters {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--border-subtle);
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
  color: var(--text-secondary);
  font-weight: 500;
}
.filter-actions {
  justify-content: flex-end;
}
.visits-table :deep(tr) {
  cursor: pointer;
}
</style>

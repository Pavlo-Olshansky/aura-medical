<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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

const router = useRouter()
const visitsStore = useVisitsStore()
const referencesStore = useReferencesStore()

const currentPage = ref(1)
const pageSize = ref(20)
const sortOrder = ref<'asc' | 'desc'>('desc')

const dateFrom = ref<Date | null>(null)
const dateTo = ref<Date | null>(null)
const selectedClinic = ref<number | null>(null)
const selectedCity = ref<number | null>(null)
const selectedProcedure = ref<number | null>(null)
const selectedPosition = ref<number | null>(null)

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

async function loadVisits() {
  const params: Record<string, any> = {
    page: currentPage.value,
    size: pageSize.value,
    sort_by: 'date',
    sort_order: sortOrder.value,
  }
  if (dateFrom.value) params.date_from = formatDateParam(dateFrom.value)
  if (dateTo.value) params.date_to = formatDateParam(dateTo.value)
  if (selectedClinic.value) params.clinic_id = selectedClinic.value
  if (selectedCity.value) params.city_id = selectedCity.value
  if (selectedProcedure.value) params.procedure_id = selectedProcedure.value
  if (selectedPosition.value) params.position_id = selectedPosition.value

  await visitsStore.fetchVisits(params)
}

function onPage(event: DataTablePageEvent) {
  currentPage.value = event.page + 1
  pageSize.value = event.rows
  loadVisits()
}

function onSort(event: DataTableSortEvent) {
  sortOrder.value = event.sortOrder === 1 ? 'asc' : 'desc'
  loadVisits()
}

function onRowClick(event: { data: Visit }) {
  router.push({ name: 'visit-detail', params: { id: event.data.id } })
}

function clearFilters() {
  dateFrom.value = null
  dateTo.value = null
  selectedClinic.value = null
  selectedCity.value = null
  selectedProcedure.value = null
  selectedPosition.value = null
  currentPage.value = 1
  loadVisits()
}

watch([dateFrom, dateTo, selectedClinic, selectedCity, selectedProcedure, selectedPosition], () => {
  currentPage.value = 1
  loadVisits()
})

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
          <Calendar v-model="dateFrom" dateFormat="dd.mm.yy" placeholder="Дата від" showIcon />
        </div>
        <div class="filter-item">
          <label>Дата до</label>
          <Calendar v-model="dateTo" dateFormat="dd.mm.yy" placeholder="Дата до" showIcon />
        </div>
        <div class="filter-item">
          <label>Клініка</label>
          <Dropdown
            v-model="selectedClinic"
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
            v-model="selectedCity"
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
            v-model="selectedProcedure"
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
            v-model="selectedPosition"
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
      :value="visitsStore.visits"
      :loading="visitsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="pageSize"
      :totalRecords="visitsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      :sortField="'date'"
      :sortOrder="sortOrder === 'asc' ? 1 : -1"
      @page="onPage"
      @sort="onSort"
      @row-click="onRowClick"
      rowHover
      stripedRows
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
      <Column header="Клініка">
        <template #body="{ data }">{{ data.clinic?.name || '-' }}</template>
      </Column>
      <Column header="Місто">
        <template #body="{ data }">{{ data.city?.name || '-' }}</template>
      </Column>
      <Column header="Документ" style="width: 80px; text-align: center">
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
  color: #e4e4e7;
  margin: 0;
}
.filters {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
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
.visits-table :deep(tr) {
  cursor: pointer;
}
</style>

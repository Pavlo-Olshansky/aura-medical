<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import Tag from 'primevue/tag'
import type { DataTablePageEvent } from 'primevue/datatable'
import { useLabResultsStore } from '@/stores/labResults'
import type { LabResult } from '@/types'
import { formatDate } from '@/utils/dateUtils'
import { useUrlFilters } from '@/composables/useUrlFilters'

const router = useRouter()
const labResultsStore = useLabResultsStore()

const filterDefs = [
  { name: 'date_from', type: 'date', default: null },
  { name: 'date_to', type: 'date', default: null },
  { name: 'page', type: 'number', default: 1 },
  { name: 'size', type: 'number', default: 20 },
] as const

const filters = useUrlFilters(filterDefs)

function formatDateParam(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function loadLabResults() {
  const params: Record<string, any> = {
    page: filters.page.value,
    size: filters.size.value,
    sort_by: 'date',
    sort_order: 'desc',
  }
  if (filters.date_from.value) params.date_from = formatDateParam(filters.date_from.value)
  if (filters.date_to.value) params.date_to = formatDateParam(filters.date_to.value)

  await labResultsStore.fetchLabResults(params)
}

function onPage(event: DataTablePageEvent) {
  filters.page.value = event.page + 1
  filters.size.value = event.rows
  filters.syncToUrl()
  loadLabResults()
}

function onRowClick(event: { data: LabResult }) {
  router.push({ name: 'lab-result-detail', params: { id: event.data.id } })
}

function clearFilters() {
  filters.clearAll()
  loadLabResults()
}

watch([filters.date_from, filters.date_to], () => {
  filters.page.value = 1
  filters.syncToUrl()
  loadLabResults()
})

onMounted(() => {
  loadLabResults()
})
</script>

<template>
  <div class="lab-results-list">
    <div class="page-header">
      <h1>Аналізи</h1>
      <Button label="Новий аналіз" icon="pi pi-plus" @click="router.push({ name: 'lab-result-create' })" />
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
        <div class="filter-item filter-actions">
          <Button label="Очистити" icon="pi pi-filter-slash" severity="secondary" text @click="clearFilters" />
        </div>
      </div>
    </div>

    <DataTable
      :value="labResultsStore.labResults"
      :loading="labResultsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="filters.size.value ?? 20"
      :totalRecords="labResultsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      @page="onPage"
      @row-click="onRowClick"
      rowHover
      stripedRows
      class="lab-results-table"
    >
      <template #empty>Аналізів не знайдено</template>
      <Column field="date" header="Дата" style="width: 130px">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column field="notes" header="Примітки">
        <template #body="{ data }">
          <span class="notes-text">{{ data.notes || '-' }}</span>
        </template>
      </Column>
      <Column header="Кількість показників" style="width: 180px; text-align: center">
        <template #body="{ data }">{{ data.entries_count ?? data.entries?.length ?? 0 }}</template>
      </Column>
      <Column header="Поза нормою" style="width: 150px; text-align: center">
        <template #body="{ data }">
          <Tag
            v-if="(data.out_of_range_count ?? 0) > 0"
            :value="String(data.out_of_range_count)"
            severity="danger"
          />
          <span v-else>0</span>
        </template>
      </Column>
      <Column header="Візит" style="width: 180px">
        <template #body="{ data }">
          <span v-if="data.visit_date">{{ formatDate(data.visit_date) }}</span>
          <span v-else>-</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.lab-results-list {
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
.notes-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}
.lab-results-table :deep(tr) {
  cursor: pointer;
}
</style>

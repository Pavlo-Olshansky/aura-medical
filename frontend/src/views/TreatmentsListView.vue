<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import type { DataTablePageEvent } from 'primevue/datatable'
import { useTreatmentsStore } from '@/stores/treatments'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDate } from '@/utils/dateUtils'
import { useUrlFilters } from '@/composables/useUrlFilters'

const router = useRouter()
const treatmentsStore = useTreatmentsStore()

const filterDefs = [
  { name: 'status', type: 'string', default: null },
  { name: 'page', type: 'number', default: 1 },
  { name: 'size', type: 'number', default: 20 },
] as const

const filters = useUrlFilters(filterDefs)

const statusOptions = [
  { label: 'В процесі', value: 'active' },
  { label: 'Готово', value: 'completed' },
]

async function loadTreatments() {
  const params: Record<string, any> = {
    page: filters.page.value,
    size: filters.size.value,
  }
  if (filters.status.value) params.status = filters.status.value

  await treatmentsStore.fetchList(params)
}

function onPage(event: DataTablePageEvent) {
  filters.page.value = event.page + 1
  filters.size.value = event.rows
  filters.syncToUrl()
  loadTreatments()
}

function onRowClick(event: { data: { id: number } }) {
  router.push({ name: 'treatment-edit', params: { id: event.data.id } })
}

watch(filters.status, () => {
  filters.page.value = 1
  filters.syncToUrl()
  loadTreatments()
})

onMounted(() => {
  loadTreatments()
})
</script>

<template>
  <div class="treatments-list">
    <div class="page-header">
      <h1>Лікування</h1>
      <Button label="Нове лікування" icon="pi pi-plus" @click="router.push({ name: 'treatment-create' })" />
    </div>

    <div class="filters">
      <div class="filter-item">
        <label>Статус</label>
        <Dropdown
          v-model="filters.status.value"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Всі статуси"
          showClear
        />
      </div>
    </div>

    <DataTable
      :value="treatmentsStore.items"
      :loading="treatmentsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="filters.size.value ?? 20"
      :totalRecords="treatmentsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      @page="onPage"
      @row-click="onRowClick"
      rowHover
      stripedRows
      scrollable
      class="treatments-table"
    >
      <template #empty>Лікувань не знайдено</template>
      <Column field="name" header="Назва" />
      <Column field="date_start" header="Дата початку">
        <template #body="{ data }">{{ formatDate(data.date_start) }}</template>
      </Column>
      <Column field="days" header="Тривалість">
        <template #body="{ data }">{{ data.days }} дн.</template>
      </Column>
      <Column field="receipt" header="Рецепт" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">
          <span class="receipt-text">{{ data.receipt || '-' }}</span>
        </template>
      </Column>
      <Column field="status" header="Статус" style="width: 130px">
        <template #body="{ data }">
          <StatusBadge :status="data.status" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.treatments-list {
  max-width: 1000px;
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
  display: flex;
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
.receipt-text {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}
.treatments-table :deep(tr) {
  cursor: pointer;
}
</style>

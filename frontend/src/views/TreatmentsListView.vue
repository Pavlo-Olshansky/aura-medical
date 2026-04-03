<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import type { DataTablePageEvent } from 'primevue/datatable'
import { useTreatmentsStore } from '@/stores/treatments'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDate } from '@/utils/dateUtils'

const router = useRouter()
const treatmentsStore = useTreatmentsStore()

const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref<'active' | 'completed' | null>(null)

const statusOptions = [
  { label: 'В процесі', value: 'active' },
  { label: 'Готово', value: 'completed' },
]

async function loadTreatments() {
  const params: Record<string, any> = {
    page: currentPage.value,
    size: pageSize.value,
  }
  if (statusFilter.value) params.status = statusFilter.value

  await treatmentsStore.fetchTreatments(params)
}

function onPage(event: DataTablePageEvent) {
  currentPage.value = event.page + 1
  pageSize.value = event.rows
  loadTreatments()
}

function onRowClick(event: { data: { id: number } }) {
  router.push({ name: 'treatment-edit', params: { id: event.data.id } })
}

watch(statusFilter, () => {
  currentPage.value = 1
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
          v-model="statusFilter"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Всі статуси"
          showClear
        />
      </div>
    </div>

    <DataTable
      :value="treatmentsStore.treatments"
      :loading="treatmentsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="pageSize"
      :totalRecords="treatmentsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      @page="onPage"
      @row-click="onRowClick"
      rowHover
      stripedRows
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
      <Column field="receipt" header="Рецепт">
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
  color: #e4e4e7;
  margin: 0;
}
.filters {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #a1a1aa;
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

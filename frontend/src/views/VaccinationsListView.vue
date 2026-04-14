<script setup lang="ts">
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useVaccinationsStore } from '@/stores/vaccinations'
import type { Vaccination } from '@/types'
import { formatDate } from '@/utils/dateUtils'
import { useListView } from '@/composables/useListView'

const router = useRouter()
const vaccinationsStore = useVaccinationsStore()

const filterDefs = [
  { name: 'page', type: 'number', default: 1 },
  { name: 'size', type: 'number', default: 20 },
] as const

function statusLabel(status: string): string {
  switch (status) {
    case 'upcoming': return 'Заплановано'
    case 'overdue': return 'Прострочено'
    case 'completed': return 'Завершено'
    default: return status
  }
}

function statusSeverity(status: string): string {
  switch (status) {
    case 'upcoming': return 'warn'
    case 'overdue': return 'danger'
    case 'completed': return 'secondary'
    default: return 'info'
  }
}

const { onPage, size: pageSize } = useListView({
  fetchList: (params) => vaccinationsStore.fetchList(params),
  filters: filterDefs,
  defaultSort: '-date',
  buildParams: (_filterValues, page, size, sort) => ({
    page,
    size,
    sort_by: 'date',
    sort_order: sort.startsWith('-') ? 'desc' : 'asc',
  }),
})

function onRowClick(event: { data: Vaccination }) {
  router.push({ name: 'vaccination-edit', params: { id: event.data.id } })
}
</script>

<template>
  <div class="vaccinations-list">
    <div class="page-header">
      <h1>Вакцинації</h1>
      <Button label="Нова вакцинація" icon="pi pi-plus" @click="router.push({ name: 'vaccination-create' })" />
    </div>

    <DataTable
      :value="vaccinationsStore.items"
      :loading="vaccinationsStore.loading"
      :lazy="true"
      :paginator="true"
      :rows="pageSize"
      :totalRecords="vaccinationsStore.total"
      :rowsPerPageOptions="[10, 20, 50]"
      @page="onPage"
      @row-click="onRowClick"
      rowHover
      stripedRows
      scrollable
      class="vaccinations-table"
    >
      <template #empty>Вакцинацій не знайдено</template>
      <Column field="date" header="Дата">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column field="vaccine_name" header="Назва вакцини" />
      <Column field="manufacturer" header="Виробник" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">{{ data.manufacturer || '-' }}</template>
      </Column>
      <Column field="dose_number" header="Доза" headerClass="hide-on-mobile" bodyClass="hide-on-mobile">
        <template #body="{ data }">{{ data.dose_number }}</template>
      </Column>
      <Column field="next_due_date" header="Наступна дата">
        <template #body="{ data }">{{ data.next_due_date ? formatDate(data.next_due_date) : '-' }}</template>
      </Column>
      <Column field="status" header="Статус" style="width: 150px">
        <template #body="{ data }">
          <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.vaccinations-list {
  max-width: 1100px;
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
.vaccinations-table :deep(tr) {
  cursor: pointer;
}
</style>

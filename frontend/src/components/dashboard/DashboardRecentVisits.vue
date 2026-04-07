<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import type { Visit, Vaccination } from '@/types'
import { formatDate } from '@/utils/dateUtils'

defineProps<{
  recentVisits: Visit[]
  loading: boolean
  overdueVaccinations: Vaccination[]
  upcomingVaccinations: Vaccination[]
}>()

const emit = defineEmits<{
  (e: 'visit-click', visit: Visit): void
  (e: 'vaccination-click', vaccination: Vaccination): void
}>()

function vaccinationStatusLabel(status: string): string {
  switch (status) {
    case 'upcoming': return 'Заплановано'
    case 'overdue': return 'Прострочено'
    case 'completed': return 'Завершено'
    default: return status
  }
}

function vaccinationStatusSeverity(status: string): string {
  switch (status) {
    case 'upcoming': return 'warn'
    case 'overdue': return 'danger'
    case 'completed': return 'secondary'
    default: return 'info'
  }
}
</script>

<template>
  <div class="section">
    <h2>Останні візити</h2>
    <DataTable
      :value="recentVisits"
      :loading="loading"
      @row-click="(event: { data: Visit }) => emit('visit-click', event.data)"
      rowHover
      stripedRows
      class="clickable-table"
    >
      <template #empty>Візитів не знайдено</template>
      <Column field="date" header="Дата">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column field="doctor" header="Лікар">
        <template #body="{ data }">{{ data.doctor || '-' }}</template>
      </Column>
      <Column header="Процедура">
        <template #body="{ data }">{{ data.procedure_name || '-' }}</template>
      </Column>
      <Column header="Клініка">
        <template #body="{ data }">{{ data.clinic_name || '-' }}</template>
      </Column>
    </DataTable>
  </div>

  <div v-if="overdueVaccinations.length > 0" class="section">
    <h2 class="overdue-header">Прострочені вакцинації</h2>
    <DataTable
      :value="overdueVaccinations"
      :loading="loading"
      @row-click="(event: { data: Vaccination }) => emit('vaccination-click', event.data)"
      rowHover
      stripedRows
      class="clickable-table"
    >
      <Column field="vaccine_name" header="Назва вакцини" />
      <Column field="date" header="Дата">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column field="next_due_date" header="Наступна дата">
        <template #body="{ data }">{{ data.next_due_date ? formatDate(data.next_due_date) : '-' }}</template>
      </Column>
      <Column header="Статус" style="width: 150px">
        <template #body="{ data }">
          <Tag :value="vaccinationStatusLabel(data.status)" :severity="vaccinationStatusSeverity(data.status)" />
        </template>
      </Column>
    </DataTable>
  </div>

  <div v-if="upcomingVaccinations.length > 0" class="section">
    <h2>Заплановані вакцинації</h2>
    <DataTable
      :value="upcomingVaccinations"
      :loading="loading"
      @row-click="(event: { data: Vaccination }) => emit('vaccination-click', event.data)"
      rowHover
      stripedRows
      class="clickable-table"
    >
      <Column field="vaccine_name" header="Назва вакцини" />
      <Column field="date" header="Дата">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column field="next_due_date" header="Наступна дата">
        <template #body="{ data }">{{ data.next_due_date ? formatDate(data.next_due_date) : '-' }}</template>
      </Column>
      <Column header="Статус" style="width: 150px">
        <template #body="{ data }">
          <Tag :value="vaccinationStatusLabel(data.status)" :severity="vaccinationStatusSeverity(data.status)" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.section h2 {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-faint);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.overdue-header {
  color: var(--danger) !important;
}
.clickable-table :deep(tr) {
  cursor: pointer;
}
</style>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDate } from '@/utils/dateUtils'

defineProps<{
  activeTreatments: any[]
  loading: boolean
}>()
</script>

<template>
  <div class="section">
    <h2>Активні лікування</h2>
    <DataTable
      :value="activeTreatments"
      :loading="loading"
      stripedRows
    >
      <template #empty>Активних лікувань немає</template>
      <Column field="name" header="Назва" />
      <Column field="date_start" header="Дата початку">
        <template #body="{ data }">{{ formatDate(data.date_start) }}</template>
      </Column>
      <Column field="days" header="Тривалість">
        <template #body="{ data }">{{ data.days }} дн.</template>
      </Column>
      <Column header="Статус" style="width: 130px">
        <template #body="{ data }">
          <StatusBadge :status="data.status" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<style scoped>
.section h2 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #52525b;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
</style>

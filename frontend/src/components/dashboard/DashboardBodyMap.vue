<script setup lang="ts">
import { computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type { DataTablePageEvent } from 'primevue/datatable'
import type { Visit } from '@/types'
import type { BodyRegionKey } from '@/components/body-map/types'
import { BODY_REGION_LABELS } from '@/components/body-map/body-regions'
import BodyMap from '@/components/body-map/BodyMap.vue'
import { formatDate } from '@/utils/dateUtils'

const props = defineProps<{
  selectedRegion: BodyRegionKey | null
  sex: string | undefined
  modalVisible: boolean
  modalVisits: Visit[]
  modalTotal: number
  modalPageSize: number
  modalLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'region-select', region: BodyRegionKey | null): void
  (e: 'modal-page', event: DataTablePageEvent): void
  (e: 'modal-row-click', visit: Visit): void
  (e: 'modal-close'): void
  (e: 'add-visit-from-modal'): void
  (e: 'update:modalVisible', value: boolean): void
}>()

const modalHeader = computed(() => {
  if (!props.selectedRegion) return ''
  const label = BODY_REGION_LABELS[props.selectedRegion] || props.selectedRegion
  return `${label} — Візити`
})
</script>

<template>
  <div class="body-map-section">
    <h2>Карта тіла</h2>
    <div class="body-map-layout">
      <BodyMap
        :selected-region="selectedRegion"
        :sex="sex"
        @select="(region: BodyRegionKey | null) => emit('region-select', region)"
      />
    </div>
  </div>

  <Dialog
    :visible="modalVisible"
    @update:visible="(val: boolean) => emit('update:modalVisible', val)"
    :header="modalHeader"
    modal
    dismissableMask
    :style="{ width: '900px' }"
    :breakpoints="{ '960px': '95vw' }"
    @hide="emit('modal-close')"
  >
    <div class="modal-toolbar">
      <Button label="Додати візит" icon="pi pi-plus" @click="emit('add-visit-from-modal')" />
    </div>
    <DataTable
      :value="modalVisits"
      :loading="modalLoading"
      :lazy="true"
      :paginator="true"
      :rows="modalPageSize"
      :totalRecords="modalTotal"
      :rowsPerPageOptions="[10, 20, 50]"
      @page="(event: DataTablePageEvent) => emit('modal-page', event)"
      @row-click="(event: { data: Visit }) => emit('modal-row-click', event.data)"
      rowHover
      stripedRows
      class="clickable-table"
    >
      <template #empty>Немає візитів для цієї ділянки</template>
      <Column field="date" header="Дата">
        <template #body="{ data }">{{ formatDate(data.date) }}</template>
      </Column>
      <Column header="Лікар">
        <template #body="{ data }">
          <span v-if="data.position">{{ data.position.name }}</span>
          <span v-if="data.position && data.doctor"> - </span>
          <span v-if="data.doctor">{{ data.doctor }}</span>
          <span v-if="!data.position && !data.doctor">-</span>
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
  </Dialog>
</template>

<style scoped>
.body-map-section {
  margin-bottom: 2rem;
}
.body-map-section h2 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #52525b;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.body-map-layout {
  background: #050505;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}
.clickable-table :deep(tr) {
  cursor: pointer;
}
.modal-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}
</style>

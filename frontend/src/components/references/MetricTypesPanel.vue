<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import type { MetricType } from '@/types'
import {
  listMetricTypes,
  createMetricType,
  updateMetricType,
  deleteMetricType,
} from '@/api/healthMetrics'

type ApiError = { response?: { data?: { detail?: string } } }

const confirm = useConfirm()
const toast = useToast()

const metricTypes = ref<MetricType[]>([])
const loading = ref(false)
const editingRows = ref<Record<number, Partial<MetricType>>>({})

const newItem = ref({
  name: '',
  unit: '',
  ref_min: null as number | null,
  ref_max: null as number | null,
  has_secondary_value: false,
  ref_min_secondary: null as number | null,
  ref_max_secondary: null as number | null,
})

async function load() {
  loading.value = true
  try {
    metricTypes.value = await listMetricTypes()
  } finally {
    loading.value = false
  }
}

function startEdit(item: MetricType) {
  editingRows.value[item.id] = {
    name: item.name,
    unit: item.unit,
    ref_min: item.ref_min,
    ref_max: item.ref_max,
    has_secondary_value: item.has_secondary_value,
    ref_min_secondary: item.ref_min_secondary,
    ref_max_secondary: item.ref_max_secondary,
  }
}

function cancelEdit(id: number) {
  delete editingRows.value[id]
}

function isEditing(id: number): boolean {
  return id in editingRows.value
}

function getEdit(id: number): Partial<MetricType> {
  return editingRows.value[id] ?? {}
}

async function saveEdit(id: number) {
  const editData = editingRows.value[id]
  if (!editData || !editData.name?.trim()) return

  try {
    const updated = await updateMetricType(id, editData)
    metricTypes.value = metricTypes.value.map((m) => (m.id === id ? updated : m))
    delete editingRows.value[id]
  } catch (e: unknown) {
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: (e as ApiError).response?.data?.detail || 'Не вдалося оновити тип показника',
      life: 5000,
    })
  }
}

async function addItem() {
  if (!newItem.value.name.trim()) return

  try {
    const created = await createMetricType(newItem.value)
    metricTypes.value.push(created)
    newItem.value = {
      name: '',
      unit: '',
      ref_min: null,
      ref_max: null,
      has_secondary_value: false,
      ref_min_secondary: null,
      ref_max_secondary: null,
    }
  } catch (e: unknown) {
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: (e as ApiError).response?.data?.detail || 'Не вдалося створити тип показника',
      life: 5000,
    })
  }
}

function confirmDelete(item: MetricType) {
  confirm.require({
    message: `Ви впевнені, що хочете видалити "${item.name}"?`,
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await deleteMetricType(item.id)
        metricTypes.value = metricTypes.value.filter((m) => m.id !== item.id)
      } catch (e: unknown) {
        toast.add({
          severity: 'error',
          summary: 'Помилка',
          detail: (e as ApiError).response?.data?.detail || 'Не вдалося видалити тип показника',
          life: 5000,
        })
      }
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="add-row metric-type-add">
    <InputText
      v-model="newItem.name"
      placeholder="Назва"
      @keyup.enter="addItem"
    />
    <InputText
      v-model="newItem.unit"
      placeholder="Одиниці"
      style="width: 100px"
    />
    <InputNumber
      v-model="newItem.ref_min"
      placeholder="Мін"
      :minFractionDigits="0"
      :maxFractionDigits="2"
      style="width: 100px"
    />
    <InputNumber
      v-model="newItem.ref_max"
      placeholder="Макс"
      :minFractionDigits="0"
      :maxFractionDigits="2"
      style="width: 100px"
    />
    <div class="checkbox-field">
      <Checkbox v-model="newItem.has_secondary_value" :binary="true" inputId="new-mt-secondary" />
      <label for="new-mt-secondary">Друге значення</label>
    </div>
    <Button
      label="Додати"
      icon="pi pi-plus"
      :disabled="!newItem.name.trim()"
      @click="addItem"
    />
  </div>

  <DataTable
    :value="metricTypes"
    :loading="loading"
    stripedRows
  >
    <template #empty>Записів не знайдено</template>
    <Column field="name" header="Назва" style="min-width: 200px">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell">
          <InputText v-model="getEdit(data.id).name" @keyup.enter="saveEdit(data.id)" />
        </div>
        <span v-else>{{ data.name }}</span>
      </template>
    </Column>
    <Column field="unit" header="Одиниці" style="width: 120px">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell">
          <InputText v-model="getEdit(data.id).unit" style="width: 80px" />
        </div>
        <span v-else>{{ data.unit || '-' }}</span>
      </template>
    </Column>
    <Column header="Мін" style="width: 100px">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell">
          <InputNumber v-model="getEdit(data.id).ref_min" :minFractionDigits="0" :maxFractionDigits="2" style="width: 80px" />
        </div>
        <span v-else>{{ data.ref_min ?? '-' }}</span>
      </template>
    </Column>
    <Column header="Макс" style="width: 100px">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell">
          <InputNumber v-model="getEdit(data.id).ref_max" :minFractionDigits="0" :maxFractionDigits="2" style="width: 80px" />
        </div>
        <span v-else>{{ data.ref_max ?? '-' }}</span>
      </template>
    </Column>
    <Column header="Друге значення" style="width: 140px; text-align: center">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="edit-cell" style="justify-content: center">
          <Checkbox v-model="getEdit(data.id).has_secondary_value" :binary="true" />
        </div>
        <i v-else-if="data.has_secondary_value" class="pi pi-check" style="color: #22c55e" />
        <span v-else>-</span>
      </template>
    </Column>
    <Column header="Дії" style="width: 150px; text-align: center">
      <template #body="{ data }">
        <div v-if="isEditing(data.id)" class="action-buttons">
          <Button icon="pi pi-check" text severity="success" @click="saveEdit(data.id)" />
          <Button icon="pi pi-times" text severity="secondary" @click="cancelEdit(data.id)" />
        </div>
        <div v-else class="action-buttons">
          <Button icon="pi pi-pencil" text severity="info" @click="startEdit(data)" />
          <Button icon="pi pi-trash" text severity="danger" @click="confirmDelete(data)" />
        </div>
      </template>
    </Column>
  </DataTable>
</template>

<style scoped>
.add-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: center;
}
.metric-type-add .p-inputtext {
  flex: unset;
}
.metric-type-add .p-inputtext:first-child {
  flex: 1;
}
.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.checkbox-field label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  white-space: nowrap;
}
.edit-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.edit-cell .p-inputtext {
  flex: 1;
}
.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}
</style>

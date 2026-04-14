<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useFormDirtyCheck } from '@/composables/useFormDirtyCheck'
import { useEnterSubmit } from '@/composables/useEnterSubmit'
import type { BiomarkerReference } from '@/types'
import {
  listBiomarkerReferences,
  createBiomarkerReference,
  updateBiomarkerReference,
  deleteBiomarkerReference,
} from '@/api/labResults'

type ApiError = { response?: { data?: { detail?: string } } }

const confirm = useConfirm()
const toast = useToast()

const items = ref<BiomarkerReference[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editItem = ref<Partial<BiomarkerReference> & { _isNew?: boolean }>({})

const { capture, setupEscapeHandler } = useFormDirtyCheck(() => ({
  name: editItem.value.name,
  abbreviation: editItem.value.abbreviation,
  unit: editItem.value.unit,
  category: editItem.value.category,
  ref_min: editItem.value.ref_min,
  ref_max: editItem.value.ref_max,
  ref_min_male: editItem.value.ref_min_male,
  ref_max_male: editItem.value.ref_max_male,
  ref_min_female: editItem.value.ref_min_female,
  ref_max_female: editItem.value.ref_max_female,
}))

setupEscapeHandler(dialogVisible, () => { dialogVisible.value = false })
useEnterSubmit(saveEdit, dialogVisible)

async function load() {
  loading.value = true
  try {
    items.value = await listBiomarkerReferences()
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editItem.value = {
    _isNew: true,
    name: '',
    abbreviation: null,
    unit: '',
    category: '',
    ref_min: null,
    ref_max: null,
    ref_min_male: null,
    ref_max_male: null,
    ref_min_female: null,
    ref_max_female: null,
  }
  dialogVisible.value = true
  nextTick(() => capture())
}

function openEdit(item: BiomarkerReference) {
  editItem.value = { ...item, _isNew: false }
  dialogVisible.value = true
  nextTick(() => capture())
}

async function saveEdit() {
  const data = editItem.value
  if (!data.name?.trim() || !data.unit?.trim()) return

  const payload = {
    name: data.name,
    abbreviation: data.abbreviation || null,
    unit: data.unit,
    category: data.category || '',
    ref_min: data.ref_min,
    ref_max: data.ref_max,
    ref_min_male: data.ref_min_male,
    ref_max_male: data.ref_max_male,
    ref_min_female: data.ref_min_female,
    ref_max_female: data.ref_max_female,
  }

  try {
    if (data._isNew) {
      const created = await createBiomarkerReference(payload)
      items.value.push(created)
    } else if (data.id) {
      const updated = await updateBiomarkerReference(data.id, payload)
      items.value = items.value.map((b) => (b.id === data.id ? updated : b))
    }
    dialogVisible.value = false
  } catch (e: unknown) {
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: (e as ApiError).response?.data?.detail || 'Не вдалося зберегти біомаркер',
      life: 5000,
    })
  }
}

function confirmDelete(item: BiomarkerReference) {
  confirm.require({
    message: `Ви впевнені, що хочете видалити "${item.name}"?`,
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await deleteBiomarkerReference(item.id)
        items.value = items.value.filter((b) => b.id !== item.id)
      } catch (e: unknown) {
        toast.add({
          severity: 'error',
          summary: 'Помилка',
          detail: (e as ApiError).response?.data?.detail || 'Не вдалося видалити біомаркер',
          life: 5000,
        })
      }
    },
  })
}

onMounted(load)
</script>

<template>
  <div class="add-row">
    <Button label="Додати біомаркер" icon="pi pi-plus" @click="openAdd" />
  </div>

  <DataTable
    :value="items"
    :loading="loading"
    stripedRows
  >
    <template #empty>Записів не знайдено</template>
    <Column field="name" header="Назва" style="min-width: 180px" />
    <Column field="abbreviation" header="Скорочення" style="width: 120px">
      <template #body="{ data }">{{ data.abbreviation || '-' }}</template>
    </Column>
    <Column field="unit" header="Одиниці" style="width: 100px" />
    <Column field="category" header="Категорія" style="width: 140px">
      <template #body="{ data }">{{ data.category || '-' }}</template>
    </Column>
    <Column header="Норма" style="width: 120px">
      <template #body="{ data }">
        <span v-if="data.ref_min != null || data.ref_max != null">
          {{ data.ref_min ?? '' }} - {{ data.ref_max ?? '' }}
        </span>
        <span v-else>-</span>
      </template>
    </Column>
    <Column header="Дії" style="width: 150px; text-align: center">
      <template #body="{ data }">
        <div class="action-buttons">
          <Button icon="pi pi-pencil" text severity="info" @click="openEdit(data)" />
          <Button icon="pi pi-trash" text severity="danger" @click="confirmDelete(data)" />
        </div>
      </template>
    </Column>
  </DataTable>

  <!-- Biomarker Edit Dialog -->
  <Dialog
    v-model:visible="dialogVisible"
    :header="editItem._isNew ? 'Новий біомаркер' : 'Редагувати біомаркер'"
    modal
    dismissableMask
    :closeOnEscape="false"
    :style="{ width: '600px' }"
    :breakpoints="{ '768px': '95vw' }"
  >
    <form class="biomarker-form" @submit.prevent="saveEdit">
      <div class="form-grid">
        <div class="form-field">
          <label>Назва *</label>
          <InputText v-model="editItem.name" placeholder="Назва біомаркера" />
        </div>
        <div class="form-field">
          <label>Скорочення</label>
          <InputText v-model="editItem.abbreviation" placeholder="Скорочення" />
        </div>
        <div class="form-field">
          <label>Одиниці *</label>
          <InputText v-model="editItem.unit" placeholder="ммоль/л" />
        </div>
        <div class="form-field">
          <label>Категорія</label>
          <InputText v-model="editItem.category" placeholder="Категорія" />
        </div>
        <div class="form-field">
          <label>Мін (загальний)</label>
          <InputNumber v-model="editItem.ref_min" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
        <div class="form-field">
          <label>Макс (загальний)</label>
          <InputNumber v-model="editItem.ref_max" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
        <div class="form-field">
          <label>Мін (чол)</label>
          <InputNumber v-model="editItem.ref_min_male" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
        <div class="form-field">
          <label>Макс (чол)</label>
          <InputNumber v-model="editItem.ref_max_male" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
        <div class="form-field">
          <label>Мін (жін)</label>
          <InputNumber v-model="editItem.ref_min_female" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
        <div class="form-field">
          <label>Макс (жін)</label>
          <InputNumber v-model="editItem.ref_max_female" :minFractionDigits="0" :maxFractionDigits="3" />
        </div>
      </div>
    </form>
    <template #footer>
      <Button label="Скасувати" severity="secondary" text @click="dialogVisible = false" />
      <Button
        label="Зберегти"
        icon="pi pi-check"
        :disabled="!editItem.name?.trim() || !editItem.unit?.trim()"
        @click="saveEdit"
      />
    </template>
  </Dialog>
</template>

<style scoped>
.add-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: center;
}
.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}
.biomarker-form .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.biomarker-form .form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.biomarker-form .form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}
</style>

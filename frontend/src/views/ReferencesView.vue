<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { useToast } from 'primevue/usetoast'
import ReferenceTable from '@/components/references/ReferenceTable.vue'
import { useReferencesStore } from '@/stores/references'
import type { ReferenceResource } from '@/api/references'
import type { Reference, MetricType, BiomarkerReference } from '@/types'
import {
  listMetricTypes,
  createMetricType,
  updateMetricType,
  deleteMetricType,
} from '@/api/healthMetrics'
import {
  listBiomarkerReferences,
  createBiomarkerReference,
  updateBiomarkerReference,
  deleteBiomarkerReference,
} from '@/api/labResults'

type ApiError = { response?: { data?: { detail?: string } } }

const referencesStore = useReferencesStore()
const activeTab = ref<string>()

onMounted(() => {
  nextTick(() => {
    activeTab.value = 'positions'
  })
})
const confirm = useConfirm()
const toast = useToast()

// ─── Simple reference tabs ───
interface TabConfig {
  label: string
  resource: ReferenceResource
  placeholder: string
}

const tabs: TabConfig[] = [
  { label: 'Позиції', resource: 'positions', placeholder: 'Нова назва...' },
  { label: 'Процедури', resource: 'procedures', placeholder: 'Нова назва...' },
  { label: 'Клініки', resource: 'clinics', placeholder: 'Нова назва...' },
  { label: 'Міста', resource: 'cities', placeholder: 'Нова назва...' },
]

function getItems(resource: ReferenceResource): Reference[] {
  return referencesStore.getList(resource)
}

async function handleCreate(resource: ReferenceResource, name: string) {
  try {
    await referencesStore.addResource(resource, name)
  } catch {
    // error is handled in the store
  }
}

async function handleUpdate(resource: ReferenceResource, id: number, name: string) {
  try {
    await referencesStore.editResource(resource, id, name)
  } catch {
    // error is handled in the store
  }
}

async function handleDelete(resource: ReferenceResource, id: number) {
  await referencesStore.removeResource(resource, id)
}

// ─── Metric Types tab ───
const metricTypes = ref<MetricType[]>([])
const metricTypesLoading = ref(false)
const editingMetricTypes = ref<Record<number, Partial<MetricType>>>({})

const newMetricType = ref({
  name: '',
  unit: '',
  ref_min: null as number | null,
  ref_max: null as number | null,
  has_secondary_value: false,
  ref_min_secondary: null as number | null,
  ref_max_secondary: null as number | null,
})

async function loadMetricTypes() {
  metricTypesLoading.value = true
  try {
    metricTypes.value = await listMetricTypes()
  } finally {
    metricTypesLoading.value = false
  }
}

function startMetricTypeEdit(item: MetricType) {
  editingMetricTypes.value[item.id] = {
    name: item.name,
    unit: item.unit,
    ref_min: item.ref_min,
    ref_max: item.ref_max,
    has_secondary_value: item.has_secondary_value,
    ref_min_secondary: item.ref_min_secondary,
    ref_max_secondary: item.ref_max_secondary,
  }
}

function cancelMetricTypeEdit(id: number) {
  delete editingMetricTypes.value[id]
}

function isMetricTypeEditing(id: number): boolean {
  return id in editingMetricTypes.value
}

function getMetricTypeEdit(id: number): Partial<MetricType> {
  return editingMetricTypes.value[id] ?? {}
}

async function saveMetricTypeEdit(id: number) {
  const editData = editingMetricTypes.value[id]
  if (!editData || !editData.name?.trim()) return

  try {
    const updated = await updateMetricType(id, editData)
    metricTypes.value = metricTypes.value.map((m) => (m.id === id ? updated : m))
    delete editingMetricTypes.value[id]
  } catch (e: unknown) {
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: (e as ApiError).response?.data?.detail || 'Не вдалося оновити тип показника',
      life: 5000,
    })
  }
}

async function addMetricType() {
  if (!newMetricType.value.name.trim()) return

  try {
    const created = await createMetricType(newMetricType.value)
    metricTypes.value.push(created)
    newMetricType.value = {
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

function confirmDeleteMetricType(item: MetricType) {
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

// ─── Biomarker References tab ───
const biomarkerRefs = ref<BiomarkerReference[]>([])
const biomarkerRefsLoading = ref(false)
const biomarkerEditDialogVisible = ref(false)
const biomarkerEditItem = ref<Partial<BiomarkerReference> & { _isNew?: boolean }>({})

async function loadBiomarkerRefs() {
  biomarkerRefsLoading.value = true
  try {
    biomarkerRefs.value = await listBiomarkerReferences()
  } finally {
    biomarkerRefsLoading.value = false
  }
}

function openBiomarkerAdd() {
  biomarkerEditItem.value = {
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
  biomarkerEditDialogVisible.value = true
}

function openBiomarkerEdit(item: BiomarkerReference) {
  biomarkerEditItem.value = {
    ...item,
    _isNew: false,
  }
  biomarkerEditDialogVisible.value = true
}

async function saveBiomarkerEdit() {
  const data = biomarkerEditItem.value
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
      biomarkerRefs.value.push(created)
    } else if (data.id) {
      const updated = await updateBiomarkerReference(data.id, payload)
      biomarkerRefs.value = biomarkerRefs.value.map((b) => (b.id === data.id ? updated : b))
    }
    biomarkerEditDialogVisible.value = false
  } catch (e: unknown) {
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: (e as ApiError).response?.data?.detail || 'Не вдалося зберегти біомаркер',
      life: 5000,
    })
  }
}

function confirmDeleteBiomarker(item: BiomarkerReference) {
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
        biomarkerRefs.value = biomarkerRefs.value.filter((b) => b.id !== item.id)
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

onMounted(async () => {
  await Promise.all([
    referencesStore.fetchAll(),
    loadMetricTypes(),
    loadBiomarkerRefs(),
  ])
})
</script>

<template>
  <div class="references-view">
    <ConfirmDialog />
    <h1>Довідники</h1>

    <TabView v-model:value="activeTab">
      <!-- Simple reference tabs -->
      <TabPanel v-for="tab in tabs" :key="tab.resource" :value="tab.resource" :header="tab.label">
        <ReferenceTable
          :items="getItems(tab.resource)"
          :title="tab.label"
          :placeholder="tab.placeholder"
          :loading="referencesStore.loading"
          @create="(name) => handleCreate(tab.resource, name)"
          @update="(id, name) => handleUpdate(tab.resource, id, name)"
          @delete="(id) => handleDelete(tab.resource, id)"
        />
      </TabPanel>

      <!-- Metric Types tab -->
      <TabPanel value="metric-types" header="Типи показників">
        <div class="add-row metric-type-add">
          <InputText
            v-model="newMetricType.name"
            placeholder="Назва"
            @keyup.enter="addMetricType"
          />
          <InputText
            v-model="newMetricType.unit"
            placeholder="Одиниці"
            style="width: 100px"
          />
          <InputNumber
            v-model="newMetricType.ref_min"
            placeholder="Мін"
            :minFractionDigits="0"
            :maxFractionDigits="2"
            style="width: 100px"
          />
          <InputNumber
            v-model="newMetricType.ref_max"
            placeholder="Макс"
            :minFractionDigits="0"
            :maxFractionDigits="2"
            style="width: 100px"
          />
          <div class="checkbox-field">
            <Checkbox v-model="newMetricType.has_secondary_value" :binary="true" inputId="new-mt-secondary" />
            <label for="new-mt-secondary">Друге значення</label>
          </div>
          <Button
            label="Додати"
            icon="pi pi-plus"
            :disabled="!newMetricType.name.trim()"
            @click="addMetricType"
          />
        </div>

        <DataTable
          :value="metricTypes"
          :loading="metricTypesLoading"
          stripedRows
        >
          <template #empty>Записів не знайдено</template>
          <Column field="name" header="Назва" style="min-width: 200px">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="edit-cell">
                <InputText v-model="getMetricTypeEdit(data.id).name" @keyup.enter="saveMetricTypeEdit(data.id)" />
              </div>
              <span v-else>{{ data.name }}</span>
            </template>
          </Column>
          <Column field="unit" header="Одиниці" style="width: 120px">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="edit-cell">
                <InputText v-model="getMetricTypeEdit(data.id).unit" style="width: 80px" />
              </div>
              <span v-else>{{ data.unit || '-' }}</span>
            </template>
          </Column>
          <Column header="Мін" style="width: 100px">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="edit-cell">
                <InputNumber v-model="getMetricTypeEdit(data.id).ref_min" :minFractionDigits="0" :maxFractionDigits="2" style="width: 80px" />
              </div>
              <span v-else>{{ data.ref_min ?? '-' }}</span>
            </template>
          </Column>
          <Column header="Макс" style="width: 100px">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="edit-cell">
                <InputNumber v-model="getMetricTypeEdit(data.id).ref_max" :minFractionDigits="0" :maxFractionDigits="2" style="width: 80px" />
              </div>
              <span v-else>{{ data.ref_max ?? '-' }}</span>
            </template>
          </Column>
          <Column header="Друге значення" style="width: 140px; text-align: center">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="edit-cell" style="justify-content: center">
                <Checkbox v-model="getMetricTypeEdit(data.id).has_secondary_value" :binary="true" />
              </div>
              <i v-else-if="data.has_secondary_value" class="pi pi-check" style="color: #22c55e" />
              <span v-else>-</span>
            </template>
          </Column>
          <Column header="Дії" style="width: 150px; text-align: center">
            <template #body="{ data }">
              <div v-if="isMetricTypeEditing(data.id)" class="action-buttons">
                <Button icon="pi pi-check" text severity="success" @click="saveMetricTypeEdit(data.id)" />
                <Button icon="pi pi-times" text severity="secondary" @click="cancelMetricTypeEdit(data.id)" />
              </div>
              <div v-else class="action-buttons">
                <Button icon="pi pi-pencil" text severity="info" @click="startMetricTypeEdit(data)" />
                <Button icon="pi pi-trash" text severity="danger" @click="confirmDeleteMetricType(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>

      <!-- Biomarker References tab -->
      <TabPanel value="biomarker-refs" header="Біомаркери">
        <div class="add-row">
          <Button label="Додати біомаркер" icon="pi pi-plus" @click="openBiomarkerAdd" />
        </div>

        <DataTable
          :value="biomarkerRefs"
          :loading="biomarkerRefsLoading"
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
                <Button icon="pi pi-pencil" text severity="info" @click="openBiomarkerEdit(data)" />
                <Button icon="pi pi-trash" text severity="danger" @click="confirmDeleteBiomarker(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
    </TabView>

    <!-- Biomarker Edit Dialog -->
    <Dialog
      v-model:visible="biomarkerEditDialogVisible"
      :header="biomarkerEditItem._isNew ? 'Новий біомаркер' : 'Редагувати біомаркер'"
      modal
      dismissableMask
      :style="{ width: '600px' }"
      :breakpoints="{ '768px': '95vw' }"
    >
      <div class="biomarker-form">
        <div class="form-grid">
          <div class="form-field">
            <label>Назва *</label>
            <InputText v-model="biomarkerEditItem.name" placeholder="Назва біомаркера" />
          </div>
          <div class="form-field">
            <label>Скорочення</label>
            <InputText v-model="biomarkerEditItem.abbreviation" placeholder="Скорочення" />
          </div>
          <div class="form-field">
            <label>Одиниці *</label>
            <InputText v-model="biomarkerEditItem.unit" placeholder="ммоль/л" />
          </div>
          <div class="form-field">
            <label>Категорія</label>
            <InputText v-model="biomarkerEditItem.category" placeholder="Категорія" />
          </div>
          <div class="form-field">
            <label>Мін (загальний)</label>
            <InputNumber v-model="biomarkerEditItem.ref_min" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
          <div class="form-field">
            <label>Макс (загальний)</label>
            <InputNumber v-model="biomarkerEditItem.ref_max" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
          <div class="form-field">
            <label>Мін (чол)</label>
            <InputNumber v-model="biomarkerEditItem.ref_min_male" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
          <div class="form-field">
            <label>Макс (чол)</label>
            <InputNumber v-model="biomarkerEditItem.ref_max_male" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
          <div class="form-field">
            <label>Мін (жін)</label>
            <InputNumber v-model="biomarkerEditItem.ref_min_female" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
          <div class="form-field">
            <label>Макс (жін)</label>
            <InputNumber v-model="biomarkerEditItem.ref_max_female" :minFractionDigits="0" :maxFractionDigits="3" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Скасувати" severity="secondary" text @click="biomarkerEditDialogVisible = false" />
        <Button
          label="Зберегти"
          icon="pi pi-check"
          :disabled="!biomarkerEditItem.name?.trim() || !biomarkerEditItem.unit?.trim()"
          @click="saveBiomarkerEdit"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.references-view {
  max-width: 1100px;
}
.references-view h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e4e4e7;
  margin-bottom: 1.5rem;
}
.add-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  align-items: center;
}
.add-row .p-inputtext {
  flex: 1;
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
  color: #a1a1aa;
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
  color: #a1a1aa;
}
</style>

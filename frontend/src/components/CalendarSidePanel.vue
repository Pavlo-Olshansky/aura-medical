<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Drawer from 'primevue/drawer'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { useReferencesStore } from '@/stores/references'
import { useVisitsStore } from '@/stores/visits'
import { BODY_REGION_OPTIONS } from '@/components/body-map/body-regions'
import { formatDateTimeForApi } from '@/utils/dateUtils'

const props = defineProps<{
  visible: boolean
  date: Date | null
  visitId: number | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
  deleted: []
}>()

const referencesStore = useReferencesStore()
const visitsStore = useVisitsStore()

const formDate = ref<Date | null>(null)
const positionId = ref<number | null>(null)
const doctor = ref('')
const procedureId = ref<number | null>(null)
const procedureDetails = ref('')
const clinicId = ref<number | null>(null)
const cityId = ref<number | null>(null)
const comment = ref('')
const link = ref('')
const bodyRegion = ref<string | null>(null)
const price = ref<number | null>(null)
const selectedFile = ref<File | null>(null)

const saving = ref(false)
const deleting = ref(false)
const errorMessage = ref('')

const isEdit = ref(false)
const panelTitle = ref('Новий візит')

watch(() => props.visible, async (newVal) => {
  if (!newVal) return

  await referencesStore.fetchAll()
  resetForm()

  if (props.visitId) {
    isEdit.value = true
    panelTitle.value = 'Редагувати візит'
    await visitsStore.fetchVisit(props.visitId)
    const v = visitsStore.currentVisit
    if (v) {
      formDate.value = new Date(v.date)
      positionId.value = v.position?.id ?? null
      doctor.value = v.doctor || ''
      procedureId.value = v.procedure?.id ?? null
      procedureDetails.value = v.procedure_details || ''
      clinicId.value = v.clinic?.id ?? null
      cityId.value = v.city?.id ?? null
      comment.value = v.comment || ''
      link.value = v.link || ''
      bodyRegion.value = (v as any).body_region || null
      price.value = v.price ?? null
    }
  } else {
    isEdit.value = false
    panelTitle.value = 'Новий візит'
    if (props.date) {
      formDate.value = new Date(props.date)
    }
  }
})

function resetForm() {
  formDate.value = null
  positionId.value = null
  doctor.value = ''
  procedureId.value = null
  procedureDetails.value = ''
  clinicId.value = null
  cityId.value = null
  comment.value = ''
  link.value = ''
  bodyRegion.value = null
  price.value = null
  selectedFile.value = null
  errorMessage.value = ''
}

function onFileSelect(event: FileUploadSelectEvent) {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0]
  }
}

async function handleSubmit() {
  if (!formDate.value) {
    errorMessage.value = "Дата є обов'язковою"
    return
  }

  saving.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('date', formatDateTimeForApi(formDate.value))
  if (positionId.value) formData.append('position_id', String(positionId.value))
  if (doctor.value) formData.append('doctor', doctor.value)
  if (procedureId.value) formData.append('procedure_id', String(procedureId.value))
  if (procedureDetails.value) formData.append('procedure_details', procedureDetails.value)
  if (clinicId.value) formData.append('clinic_id', String(clinicId.value))
  if (cityId.value) formData.append('city_id', String(cityId.value))
  if (comment.value) formData.append('comment', comment.value)
  if (link.value) formData.append('link', link.value)
  if (bodyRegion.value) formData.append('body_region', bodyRegion.value)
  if (price.value !== null) formData.append('price', String(price.value))
  if (selectedFile.value) formData.append('document', selectedFile.value)

  try {
    if (isEdit.value && props.visitId) {
      await visitsStore.updateVisit(props.visitId, formData)
    } else {
      await visitsStore.createVisit(formData)
    }
    emit('saved')
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || 'Помилка збереження'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!props.visitId) return
  deleting.value = true
  try {
    await visitsStore.deleteVisit(props.visitId)
    emit('deleted')
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || 'Помилка видалення'
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <Drawer
    :visible="visible"
    position="right"
    :header="panelTitle"
    class="calendar-side-panel"
    @update:visible="(v: boolean) => { if (!v) emit('close') }"
  >
    <form class="panel-form" @submit.prevent="handleSubmit">
      <div class="form-field">
        <label>Дата *</label>
        <Calendar
          v-model="formDate"
          dateFormat="dd.mm.yy"
          showTime
          hourFormat="24"
          showIcon
          placeholder="Оберіть дату"
        />
      </div>

      <div class="form-field">
        <label>Позиція</label>
        <Dropdown
          v-model="positionId"
          :options="referencesStore.positions"
          optionLabel="name"
          optionValue="id"
          placeholder="Позиція"
          showClear
        />
      </div>

      <div class="form-field">
        <label>Лікар</label>
        <InputText v-model="doctor" placeholder="Ім'я лікаря" />
      </div>

      <div class="form-field">
        <label>Процедура</label>
        <Dropdown
          v-model="procedureId"
          :options="referencesStore.procedures"
          optionLabel="name"
          optionValue="id"
          placeholder="Процедура"
          showClear
        />
      </div>

      <div class="form-field">
        <label>Деталі процедури</label>
        <Textarea v-model="procedureDetails" rows="2" placeholder="Деталі" />
      </div>

      <div class="form-field">
        <label>Клініка</label>
        <Dropdown
          v-model="clinicId"
          :options="referencesStore.clinics"
          optionLabel="name"
          optionValue="id"
          placeholder="Клініка"
          showClear
        />
      </div>

      <div class="form-field">
        <label>Місто</label>
        <Dropdown
          v-model="cityId"
          :options="referencesStore.cities"
          optionLabel="name"
          optionValue="id"
          placeholder="Місто"
          showClear
        />
      </div>

      <div class="form-field">
        <label>Ділянка тіла</label>
        <Dropdown
          v-model="bodyRegion"
          :options="BODY_REGION_OPTIONS"
          optionLabel="label"
          optionValue="value"
          placeholder="Ділянка"
          showClear
        />
      </div>

      <div class="form-field">
        <label>Вартість</label>
        <InputNumber v-model="price" mode="decimal" :maxFractionDigits="2" placeholder="Вартість" />
      </div>

      <div class="form-field">
        <label>Коментар</label>
        <Textarea v-model="comment" rows="2" placeholder="Коментар" />
      </div>

      <div class="form-field">
        <label>Посилання</label>
        <InputText v-model="link" placeholder="https://..." />
      </div>

      <div class="form-field">
        <label>Документ</label>
        <FileUpload mode="basic" :auto="false" chooseLabel="Обрати файл" @select="onFileSelect" />
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div class="panel-actions">
        <Button type="submit" :label="isEdit ? 'Зберегти' : 'Створити'" icon="pi pi-check" :loading="saving" />
        <Button
          v-if="isEdit"
          label="Видалити"
          icon="pi pi-trash"
          severity="danger"
          outlined
          :loading="deleting"
          @click="handleDelete"
        />
        <Button label="Скасувати" severity="secondary" text @click="emit('close')" />
      </div>
    </form>
  </Drawer>
</template>

<style scoped>
.panel-form {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.form-field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.error-message {
  color: #dc2626;
  font-size: 0.8rem;
}
.panel-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
}
</style>

<style>
.calendar-side-panel {
  width: 380px !important;
}
@media (max-width: 768px) {
  .calendar-side-panel {
    width: 100% !important;
  }
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { useVisitsStore } from '@/stores/visits'
import { useReferencesStore } from '@/stores/references'
import { isDemoMode } from '@/stores/auth'
import { BODY_REGION_OPTIONS, SPECIALTY_REGION_MAP } from '@/components/body-map/body-regions'
import { formatDateTimeForApi } from '@/utils/dateUtils'
import { useEnterSubmit } from '@/composables/useEnterSubmit'
import { useFormSubmit } from '@/composables/useFormSubmit'

const route = useRoute()
const router = useRouter()
const visitsStore = useVisitsStore()
const referencesStore = useReferencesStore()

const editId = computed(() => (route.params.id ? Number(route.params.id) : undefined))
const isEdit = computed(() => editId.value !== undefined)
const pageTitle = computed(() => (isEdit.value ? 'Редагувати візит' : 'Новий візит'))

const date = ref<Date | null>(null)
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

const textareaFocused = ref(false)

const { submitting: saving, error: errorMessage, handleSubmit } = useFormSubmit<FormData>({
  store: {
    create: (data) => visitsStore.create(data),
    update: (id, data) => visitsStore.update(id, data),
  },
  buildPayload: () => {
    const formData = new FormData()
    formData.append('date', formatDateTimeForApi(date.value!))
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
    return formData
  },
  validate: () => {
    if (!date.value) return 'Дата є обов\'язковою'
    return null
  },
  successRoute: { name: 'visits' },
  entityLabel: 'Візит',
  isEdit,
  editId,
})

useEnterSubmit(handleSubmit)

// Auto-suggest body region when position changes
watch(positionId, (newVal) => {
  if (!newVal || isEdit.value) return
  const position = referencesStore.positions.find((p: { id: number }) => p.id === newVal)
  if (!position) return
  const regions = SPECIALTY_REGION_MAP[position.name]
  if (regions && regions.length === 1 && regions[0]) {
    bodyRegion.value = regions[0]
  }
})

function onFileSelect(event: FileUploadSelectEvent) {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0]
  }
}

function onFileClear() {
  selectedFile.value = null
}

onMounted(async () => {
  await referencesStore.fetchAll()

  // Pre-fill body region from query param (e.g. from body map modal)
  const queryRegion = route.query.body_region as string | undefined
  if (queryRegion && !isEdit.value) {
    bodyRegion.value = queryRegion
  }

  if (isEdit.value && editId.value) {
    await visitsStore.fetchOne(editId.value)
    const visit = visitsStore.currentItem
    if (visit) {
      date.value = new Date(visit.date)
      positionId.value = visit.position?.id ?? null
      doctor.value = visit.doctor || ''
      procedureId.value = visit.procedure?.id ?? null
      procedureDetails.value = visit.procedure_details || ''
      clinicId.value = visit.clinic?.id ?? null
      cityId.value = visit.city?.id ?? null
      comment.value = visit.comment || ''
      link.value = visit.link || ''
      bodyRegion.value = (visit as any).body_region || null
      price.value = visit.price ?? null
    }
  }
})
</script>

<template>
  <div class="visit-form">
    <div class="page-header">
      <h1>{{ pageTitle }}</h1>
      <Button label="Назад" icon="pi pi-arrow-left" severity="secondary" text @click="router.back()" />
    </div>

    <form class="form-card" @submit.prevent="handleSubmit">
      <div class="form-grid">
        <div class="form-field">
          <label for="date">Дата *</label>
          <Calendar
            id="date"
            v-model="date"
            dateFormat="dd.mm.yy"
            showTime
            hourFormat="24"
            showIcon
            placeholder="Оберіть дату та час"
          />
        </div>

        <div class="form-field">
          <label for="position">Позиція</label>
          <Dropdown
            id="position"
            v-model="positionId"
            :options="referencesStore.positions"
            optionLabel="name"
            optionValue="id"
            placeholder="Оберіть позицію"
            showClear
          />
        </div>

        <div class="form-field">
          <label for="doctor">Лікар</label>
          <InputText id="doctor" v-model="doctor" placeholder="Ім'я лікаря" />
        </div>

        <div class="form-field">
          <label for="procedure">Процедура</label>
          <Dropdown
            id="procedure"
            v-model="procedureId"
            :options="referencesStore.procedures"
            optionLabel="name"
            optionValue="id"
            placeholder="Оберіть процедуру"
            showClear
          />
        </div>

        <div class="form-field full-width">
          <label for="procedureDetails">Деталі процедури</label>
          <Textarea
            id="procedureDetails"
            v-model="procedureDetails"
            rows="3"
            placeholder="Деталі процедури"
            @focus="textareaFocused = true"
            @blur="textareaFocused = false"
            @keydown.ctrl.enter.prevent="handleSubmit"
            @keydown.meta.enter.prevent="handleSubmit"
          />
        </div>

        <div class="form-field">
          <label for="clinic">Клініка</label>
          <Dropdown
            id="clinic"
            v-model="clinicId"
            :options="referencesStore.clinics"
            optionLabel="name"
            optionValue="id"
            placeholder="Оберіть клініку"
            showClear
          />
        </div>

        <div class="form-field">
          <label for="city">Місто</label>
          <Dropdown
            id="city"
            v-model="cityId"
            :options="referencesStore.cities"
            optionLabel="name"
            optionValue="id"
            placeholder="Оберіть місто"
            showClear
          />
        </div>

        <div class="form-field">
          <label for="bodyRegion">Ділянка тіла</label>
          <Dropdown
            id="bodyRegion"
            v-model="bodyRegion"
            :options="BODY_REGION_OPTIONS"
            optionLabel="label"
            optionValue="value"
            placeholder="Оберіть ділянку"
            showClear
          />
        </div>

        <div class="form-field">
          <label for="price">Вартість</label>
          <InputNumber id="price" v-model="price" mode="decimal" :maxFractionDigits="2" placeholder="Вартість" />
        </div>

        <div class="form-field full-width">
          <label for="comment">Коментар</label>
          <Textarea
            id="comment"
            v-model="comment"
            rows="3"
            placeholder="Коментар до візиту"
            @focus="textareaFocused = true"
            @blur="textareaFocused = false"
            @keydown.ctrl.enter.prevent="handleSubmit"
            @keydown.meta.enter.prevent="handleSubmit"
          />
        </div>

        <div class="form-field full-width">
          <label for="link">Посилання</label>
          <InputText id="link" v-model="link" placeholder="https://..." />
        </div>

        <div class="form-field full-width">
          <label>Документ</label>
          <FileUpload
            mode="basic"
            :auto="false"
            chooseLabel="Обрати файл"
            @select="onFileSelect"
            @clear="onFileClear"
          />
          <small v-if="isEdit && visitsStore.currentItem?.document" class="existing-file">
            Поточний файл: {{ visitsStore.currentItem.document.split('/').pop() }}
          </small>
        </div>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <p v-if="isDemoMode" class="demo-notice">
        <i class="pi pi-info-circle" /> Зміни не зберігаються в демо-режимі
      </p>

      <div class="form-actions">
        <Button type="submit" :label="(isEdit ? 'Зберегти' : 'Створити') + (textareaFocused ? ' (Ctrl+Enter)' : '')" icon="pi pi-check" :loading="saving" />
        <Button label="Скасувати" severity="secondary" outlined @click="router.back()" />
      </div>
    </form>
  </div>
</template>

<style scoped>
.visit-form {
  max-width: 800px;
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
.form-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.75rem;
  padding: 2rem;
  border: 1px solid var(--border-subtle);
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.form-field.full-width {
  grid-column: 1 / -1;
}
.form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.existing-file {
  color: var(--text-faint);
  margin-top: 0.25rem;
}
.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 1rem;
}
.demo-notice {
  color: #ca8a04;
  background: rgba(250, 204, 21, 0.1);
  border-left: 3px solid #facc15;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-field.full-width {
    grid-column: auto;
  }
}
</style>

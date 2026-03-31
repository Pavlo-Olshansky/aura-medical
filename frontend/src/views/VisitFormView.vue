<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { useVisitsStore } from '@/stores/visits'
import { useReferencesStore } from '@/stores/references'
import { BODY_REGION_OPTIONS, SPECIALTY_REGION_MAP } from '@/components/body-map/body-regions'

const route = useRoute()
const router = useRouter()
const visitsStore = useVisitsStore()
const referencesStore = useReferencesStore()

const editId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => editId.value !== null)
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
const selectedFile = ref<File | null>(null)

const saving = ref(false)
const errorMessage = ref('')

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

function formatDateForApi(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function handleSubmit() {
  if (!date.value) {
    errorMessage.value = 'Дата є обов\'язковою'
    return
  }

  saving.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('date', formatDateForApi(date.value))
  if (positionId.value) formData.append('position_id', String(positionId.value))
  if (doctor.value) formData.append('doctor', doctor.value)
  if (procedureId.value) formData.append('procedure_id', String(procedureId.value))
  if (procedureDetails.value) formData.append('procedure_details', procedureDetails.value)
  if (clinicId.value) formData.append('clinic_id', String(clinicId.value))
  if (cityId.value) formData.append('city_id', String(cityId.value))
  if (comment.value) formData.append('comment', comment.value)
  if (link.value) formData.append('link', link.value)
  if (bodyRegion.value) formData.append('body_region', bodyRegion.value)
  if (selectedFile.value) formData.append('document', selectedFile.value)

  try {
    if (isEdit.value && editId.value) {
      await visitsStore.updateVisit(editId.value, formData)
      router.push({ name: 'visit-detail', params: { id: editId.value } })
    } else {
      const visit = await visitsStore.createVisit(formData)
      router.push({ name: 'visit-detail', params: { id: visit.id } })
    }
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || 'Помилка збереження візиту'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await referencesStore.fetchAll()

  if (isEdit.value && editId.value) {
    await visitsStore.fetchVisit(editId.value)
    const visit = visitsStore.currentVisit
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
            showIcon
            placeholder="Оберіть дату"
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
          <Textarea id="procedureDetails" v-model="procedureDetails" rows="3" placeholder="Деталі процедури" />
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

        <div class="form-field full-width">
          <label for="comment">Коментар</label>
          <Textarea id="comment" v-model="comment" rows="3" placeholder="Коментар до візиту" />
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
          <small v-if="isEdit && visitsStore.currentVisit?.document" class="existing-file">
            Поточний файл: {{ visitsStore.currentVisit.document.split('/').pop() }}
          </small>
        </div>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div class="form-actions">
        <Button type="submit" :label="isEdit ? 'Зберегти' : 'Створити'" icon="pi pi-check" :loading="saving" />
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
  color: #1e293b;
  margin: 0;
}
.form-card {
  background: #fff;
  border-radius: 0.75rem;
  padding: 2rem;
  border: 1px solid #e2e8f0;
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
  color: #374151;
}
.existing-file {
  color: #64748b;
  margin-top: 0.25rem;
}
.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 1rem;
}
.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}
</style>

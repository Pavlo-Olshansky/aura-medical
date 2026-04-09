<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Calendar from 'primevue/calendar'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { useVaccinationsStore } from '@/stores/vaccinations'
import { useConfirm } from 'primevue/useconfirm'
import AppConfirmDialog from '@/components/AppConfirmDialog.vue'
import { formatDateForApi } from '@/utils/dateUtils'

const route = useRoute()
const router = useRouter()
const vaccinationsStore = useVaccinationsStore()
const confirm = useConfirm()

const editId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => editId.value !== null)
const pageTitle = computed(() => (isEdit.value ? 'Редагувати вакцинацію' : 'Нова вакцинація'))

const vaccineName = ref('')
const date = ref<Date | null>(null)
const manufacturer = ref('')
const lotNumber = ref('')
const doseNumber = ref<number | null>(1)
const nextDueDate = ref<Date | null>(null)
const notes = ref('')
const selectedFile = ref<File | null>(null)

const saving = ref(false)
const errorMessage = ref('')

function onFileSelect(event: FileUploadSelectEvent) {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0]
  }
}

function onFileClear() {
  selectedFile.value = null
}

async function handleSubmit() {
  if (!vaccineName.value.trim()) {
    errorMessage.value = 'Назва вакцини є обов\'язковою'
    return
  }
  if (!date.value) {
    errorMessage.value = 'Дата є обов\'язковою'
    return
  }
  if (!doseNumber.value || doseNumber.value < 1) {
    errorMessage.value = 'Номер дози має бути більше 0'
    return
  }

  saving.value = true
  errorMessage.value = ''

  const formData = new FormData()
  formData.append('vaccine_name', vaccineName.value)
  formData.append('date', formatDateForApi(date.value))
  formData.append('dose_number', String(doseNumber.value))
  if (manufacturer.value) formData.append('manufacturer', manufacturer.value)
  if (lotNumber.value) formData.append('lot_number', lotNumber.value)
  if (nextDueDate.value) formData.append('next_due_date', formatDateForApi(nextDueDate.value))
  if (notes.value) formData.append('notes', notes.value)
  if (selectedFile.value) formData.append('document', selectedFile.value)

  try {
    if (isEdit.value && editId.value) {
      await vaccinationsStore.updateVaccination(editId.value, formData)
    } else {
      await vaccinationsStore.createVaccination(formData)
    }
    router.push({ name: 'vaccinations' })
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || 'Помилка збереження вакцинації'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!editId.value) return
  confirm.require({
    message: 'Ви впевнені, що хочете видалити цю вакцинацію?',
    header: 'Підтвердження видалення',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Видалити',
    rejectLabel: 'Скасувати',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await vaccinationsStore.deleteVaccination(editId.value!)
      router.push({ name: 'vaccinations' })
    },
  })
}

onMounted(async () => {
  if (isEdit.value && editId.value) {
    await vaccinationsStore.fetchVaccination(editId.value)
    const vaccination = vaccinationsStore.currentVaccination
    if (vaccination) {
      vaccineName.value = vaccination.vaccine_name
      date.value = new Date(vaccination.date)
      manufacturer.value = vaccination.manufacturer || ''
      lotNumber.value = vaccination.lot_number || ''
      doseNumber.value = vaccination.dose_number
      nextDueDate.value = vaccination.next_due_date ? new Date(vaccination.next_due_date) : null
      notes.value = vaccination.notes || ''
    }
  }
})
</script>

<template>
  <div class="vaccination-form">
    <AppConfirmDialog />
    <div class="page-header">
      <h1>{{ pageTitle }}</h1>
      <div class="header-actions">
        <Button
          v-if="isEdit"
          label="Видалити"
          icon="pi pi-trash"
          severity="danger"
          outlined
          @click="handleDelete"
        />
        <Button label="Назад" icon="pi pi-arrow-left" severity="secondary" text @click="router.back()" />
      </div>
    </div>

    <form class="form-card" @submit.prevent="handleSubmit">
      <div class="form-grid">
        <div class="form-field full-width">
          <label for="vaccineName">Назва вакцини *</label>
          <InputText id="vaccineName" v-model="vaccineName" placeholder="Назва вакцини" />
        </div>

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
          <label for="manufacturer">Виробник</label>
          <InputText id="manufacturer" v-model="manufacturer" placeholder="Виробник вакцини" />
        </div>

        <div class="form-field">
          <label for="lotNumber">Номер партії</label>
          <InputText id="lotNumber" v-model="lotNumber" placeholder="Номер партії" />
        </div>

        <div class="form-field">
          <label for="doseNumber">Номер дози *</label>
          <InputNumber id="doseNumber" v-model="doseNumber" :min="1" placeholder="Номер дози" />
        </div>

        <div class="form-field">
          <label for="nextDueDate">Наступна дата</label>
          <Calendar
            id="nextDueDate"
            v-model="nextDueDate"
            dateFormat="dd.mm.yy"
            showIcon
            placeholder="Наступна дата"
          />
        </div>

        <div class="form-field full-width">
          <label for="notes">Примітки</label>
          <Textarea id="notes" v-model="notes" rows="3" placeholder="Примітки" />
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
          <small v-if="isEdit && vaccinationsStore.currentVaccination?.has_document" class="existing-file">
            Документ вже прикріплено
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
.vaccination-form {
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
.header-actions {
  display: flex;
  gap: 0.5rem;
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

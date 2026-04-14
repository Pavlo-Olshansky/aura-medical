<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Calendar from 'primevue/calendar'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { useTreatmentsStore } from '@/stores/treatments'
import { isDemoMode } from '@/stores/auth'
import AppConfirmDialog from '@/components/AppConfirmDialog.vue'
import { formatDateForApi } from '@/utils/dateUtils'
import { useEnterSubmit } from '@/composables/useEnterSubmit'
import { useFormSubmit } from '@/composables/useFormSubmit'

interface TreatmentPayload {
  name: string
  date_start: string
  days: number
  receipt: string
}

const route = useRoute()
const router = useRouter()
const treatmentsStore = useTreatmentsStore()

const editId = computed(() => (route.params.id ? Number(route.params.id) : undefined))
const isEdit = computed(() => editId.value !== undefined)
const pageTitle = computed(() => (isEdit.value ? 'Редагувати лікування' : 'Нове лікування'))

const name = ref('')
const dateStart = ref<Date | null>(null)
const days = ref<number | null>(null)
const receipt = ref('')

const textareaFocused = ref(false)

const { submitting: saving, error: errorMessage, handleSubmit, handleDelete } = useFormSubmit<TreatmentPayload>({
  store: {
    create: (data) => treatmentsStore.create(data),
    update: (id, data) => treatmentsStore.update(id, data),
    remove: (id) => treatmentsStore.remove(id),
  },
  buildPayload: () => ({
    name: name.value,
    date_start: formatDateForApi(dateStart.value!),
    days: days.value!,
    receipt: receipt.value,
  }),
  validate: () => {
    if (!name.value.trim()) return 'Назва є обов\'язковою'
    if (!dateStart.value) return 'Дата початку є обов\'язковою'
    if (!days.value || days.value < 1) return 'Тривалість має бути більше 0'
    return null
  },
  successRoute: { name: 'treatments' },
  entityLabel: 'Лікування',
  isEdit,
  editId,
})

useEnterSubmit(handleSubmit)

onMounted(async () => {
  if (isEdit.value && editId.value) {
    await treatmentsStore.fetchOne(editId.value)
    const treatment = treatmentsStore.currentItem
    if (treatment) {
      name.value = treatment.name
      dateStart.value = new Date(treatment.date_start)
      days.value = treatment.days
      receipt.value = treatment.receipt || ''
    }
  }
})
</script>

<template>
  <div class="treatment-form">
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
          <label for="name">Назва *</label>
          <InputText id="name" v-model="name" placeholder="Назва лікування" />
        </div>

        <div class="form-field">
          <label for="dateStart">Дата початку *</label>
          <Calendar
            id="dateStart"
            v-model="dateStart"
            dateFormat="dd.mm.yy"
            showIcon
            placeholder="Оберіть дату"
          />
        </div>

        <div class="form-field">
          <label for="days">Тривалість (днів) *</label>
          <InputNumber id="days" v-model="days" :min="1" placeholder="Кількість днів" />
        </div>

        <div class="form-field full-width">
          <label for="receipt">Рецепт</label>
          <Textarea
            id="receipt"
            v-model="receipt"
            rows="4"
            placeholder="Опис рецепту"
            @focus="textareaFocused = true"
            @blur="textareaFocused = false"
            @keydown.ctrl.enter.prevent="handleSubmit"
            @keydown.meta.enter.prevent="handleSubmit"
          />
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
.treatment-form {
  max-width: 700px;
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

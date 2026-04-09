<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import AutoComplete from 'primevue/autocomplete'
import Button from 'primevue/button'
import { useLabResultsStore } from '@/stores/labResults'
import { useVisitsStore } from '@/stores/visits'
import { useAuthStore } from '@/stores/auth'
import type { BiomarkerReference } from '@/types'
import { formatDateForApi } from '@/utils/dateUtils'
import { useEnterSubmit } from '@/composables/useEnterSubmit'

const route = useRoute()
const router = useRouter()
const labResultsStore = useLabResultsStore()
const visitsStore = useVisitsStore()
const authStore = useAuthStore()

const editId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => editId.value !== null)
const pageTitle = computed(() => (isEdit.value ? 'Редагувати аналіз' : 'Новий аналіз'))

const date = ref<Date | null>(null)
const visitId = ref<number | null>(null)
const notes = ref('')

interface EntryRow {
  biomarkerRef: BiomarkerReference | null
  biomarkerName: string
  value: number | null
  unit: string
  ref_min: number | null
  ref_max: number | null
}

const entries = ref<EntryRow[]>([])
const filteredBiomarkers = ref<BiomarkerReference[]>([])

const saving = ref(false)
const errorMessage = ref('')
const textareaFocused = ref(false)

useEnterSubmit(handleSubmit)

function formatVisitLabel(visit: { id: number; date: string; procedure?: { name: string } | null }): string {
  const d = new Date(visit.date)
  const dateStr = d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
  const proc = visit.procedure?.name || ''
  return proc ? `${dateStr} - ${proc}` : dateStr
}

function addEntry() {
  entries.value.push({
    biomarkerRef: null,
    biomarkerName: '',
    value: null,
    unit: '',
    ref_min: null,
    ref_max: null,
  })
}

function removeEntry(index: number) {
  entries.value.splice(index, 1)
}

function onBiomarkerSelect(index: number, biomarker: BiomarkerReference) {
  const entry = entries.value[index]
  if (!entry) return
  entry.biomarkerRef = biomarker
  entry.biomarkerName = biomarker.name
  entry.unit = biomarker.unit

  const userSex = authStore.user?.sex
  if (userSex === 'male' && biomarker.ref_min_male != null) {
    entry.ref_min = biomarker.ref_min_male
  } else if (userSex === 'female' && biomarker.ref_min_female != null) {
    entry.ref_min = biomarker.ref_min_female
  } else {
    entry.ref_min = biomarker.ref_min
  }

  if (userSex === 'male' && biomarker.ref_max_male != null) {
    entry.ref_max = biomarker.ref_max_male
  } else if (userSex === 'female' && biomarker.ref_max_female != null) {
    entry.ref_max = biomarker.ref_max_female
  } else {
    entry.ref_max = biomarker.ref_max
  }
}

async function searchBiomarkers(event: { query: string }) {
  await labResultsStore.fetchBiomarkerReferences(event.query)
  filteredBiomarkers.value = labResultsStore.biomarkerReferences
}

async function handleSubmit() {
  if (!date.value) {
    errorMessage.value = 'Дата є обов\'язковою'
    return
  }

  const validEntries = entries.value.filter((e) => e.biomarkerName.trim() && e.value != null)
  if (validEntries.length === 0) {
    errorMessage.value = 'Додайте хоча б один показник'
    return
  }

  saving.value = true
  errorMessage.value = ''

  const payload = {
    date: formatDateForApi(date.value),
    visit_id: visitId.value,
    notes: notes.value || null,
    entries: validEntries.map((e) => ({
      biomarker_id: e.biomarkerRef?.id || null,
      biomarker_name: e.biomarkerName,
      value: e.value,
      unit: e.unit,
      ref_min: e.ref_min,
      ref_max: e.ref_max,
    })),
  }

  try {
    if (isEdit.value && editId.value) {
      await labResultsStore.updateLabResult(editId.value, payload)
      router.push({ name: 'lab-results' })
    } else {
      await labResultsStore.createLabResult(payload)
      router.push({ name: 'lab-results' })
    }
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || 'Помилка збереження аналізу'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await authStore.fetchUser()
  await labResultsStore.fetchBiomarkerReferences()

  // Load visits for the dropdown
  await visitsStore.fetchVisits({ page: 1, size: 100, sort_by: 'date', sort_order: 'desc' })

  if (isEdit.value && editId.value) {
    await labResultsStore.fetchLabResult(editId.value)
    const labResult = labResultsStore.currentLabResult
    if (labResult) {
      date.value = new Date(labResult.date)
      visitId.value = labResult.visit_id
      notes.value = labResult.notes || ''
      entries.value = labResult.entries.map((e) => ({
        biomarkerRef: e.biomarker_id
          ? (labResultsStore.biomarkerReferences.find((b) => b.id === e.biomarker_id) || null)
          : null,
        biomarkerName: e.biomarker_name,
        value: e.value,
        unit: e.unit,
        ref_min: e.ref_min,
        ref_max: e.ref_max,
      }))
    }
  }

  if (entries.value.length === 0) {
    addEntry()
  }
})
</script>

<template>
  <div class="lab-result-form">
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
          <label for="visit">Візит</label>
          <Dropdown
            id="visit"
            v-model="visitId"
            :options="visitsStore.visits"
            :optionLabel="(v: any) => formatVisitLabel(v)"
            optionValue="id"
            placeholder="Оберіть візит"
            showClear
          />
        </div>

        <div class="form-field full-width">
          <label for="notes">Примітки</label>
          <Textarea
            id="notes"
            v-model="notes"
            rows="3"
            placeholder="Примітки до аналізу"
            @focus="textareaFocused = true"
            @blur="textareaFocused = false"
            @keydown.ctrl.enter.prevent="handleSubmit"
            @keydown.meta.enter.prevent="handleSubmit"
          />
        </div>
      </div>

      <div class="entries-section">
        <div class="entries-header">
          <h3>Показники</h3>
          <Button label="Додати показник" icon="pi pi-plus" severity="secondary" outlined size="small" @click="addEntry" />
        </div>

        <div
          v-for="(entry, index) in entries"
          :key="index"
          class="entry-row"
        >
          <div class="entry-field entry-biomarker">
            <label>Біомаркер</label>
            <AutoComplete
              v-model="entry.biomarkerName"
              :suggestions="filteredBiomarkers"
              optionLabel="name"
              placeholder="Назва біомаркера"
              @complete="searchBiomarkers"
              @item-select="(e: any) => onBiomarkerSelect(index, e.value)"
              :forceSelection="false"
            />
          </div>
          <div class="entry-field entry-value">
            <label>Значення</label>
            <InputNumber
              v-model="entry.value"
              :minFractionDigits="0"
              :maxFractionDigits="4"
              placeholder="0"
            />
          </div>
          <div class="entry-field entry-unit">
            <label>Одиниця</label>
            <InputText v-model="entry.unit" placeholder="од." />
          </div>
          <div class="entry-field entry-ref">
            <label>Мін</label>
            <InputNumber
              v-model="entry.ref_min"
              :minFractionDigits="0"
              :maxFractionDigits="4"
              placeholder="-"
            />
          </div>
          <div class="entry-field entry-ref">
            <label>Макс</label>
            <InputNumber
              v-model="entry.ref_max"
              :minFractionDigits="0"
              :maxFractionDigits="4"
              placeholder="-"
            />
          </div>
          <div class="entry-field entry-delete">
            <label>&nbsp;</label>
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              @click="removeEntry(index)"
              :disabled="entries.length <= 1"
            />
          </div>
        </div>
      </div>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div class="form-actions">
        <Button type="submit" :label="(isEdit ? 'Зберегти' : 'Створити') + (textareaFocused ? ' (Ctrl+Enter)' : '')" icon="pi pi-check" :loading="saving" />
        <Button label="Скасувати" severity="secondary" outlined @click="router.back()" />
      </div>
    </form>
  </div>
</template>

<style scoped>
.lab-result-form {
  max-width: 1000px;
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
.entries-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}
.entries-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.entries-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.entry-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.entry-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.entry-field label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-muted);
}
.entry-biomarker {
  flex: 2;
}
.entry-value {
  flex: 1;
}
.entry-unit {
  flex: 0.8;
}
.entry-ref {
  flex: 0.7;
}
.entry-delete {
  flex: 0;
  min-width: 40px;
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
  .entry-row {
    flex-wrap: wrap;
  }
  .entry-biomarker {
    flex: 1 1 100%;
  }
  .entry-value,
  .entry-unit,
  .entry-ref {
    flex: 1 1 auto;
  }
}
</style>

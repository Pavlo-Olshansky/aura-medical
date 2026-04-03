<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { apiClient } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import type { ProfileData } from '@/types'
import { formatDateForApi } from '@/utils/dateUtils'

const toast = useToast()
const auth = useAuthStore()

const loading = ref(true)
const saving = ref(false)

const sex = ref<string>('male')
const dateOfBirth = ref<Date | null>(null)
const heightCm = ref<number | null>(null)
const weightKg = ref<number | null>(null)
const bloodType = ref<string | null>(null)
const allergies = ref<string | null>(null)
const chronicConditions = ref<string | null>(null)
const emergencyContactName = ref<string | null>(null)
const emergencyContactPhone = ref<string | null>(null)

const sexOptions = [
  { label: 'Чоловіча', value: 'male' },
  { label: 'Жіноча', value: 'female' },
]

const bloodTypeOptions = [
  { label: 'A+', value: 'A+' },
  { label: 'A−', value: 'A-' },
  { label: 'B+', value: 'B+' },
  { label: 'B−', value: 'B-' },
  { label: 'AB+', value: 'AB+' },
  { label: 'AB−', value: 'AB-' },
  { label: 'O+', value: 'O+' },
  { label: 'O−', value: 'O-' },
]

const calculatedAge = computed(() => {
  if (!dateOfBirth.value) return null
  const today = new Date()
  const birth = dateOfBirth.value
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age
})

function populateForm(data: ProfileData) {
  sex.value = data.sex
  dateOfBirth.value = data.date_of_birth ? new Date(data.date_of_birth + 'T00:00:00') : null
  heightCm.value = data.height_cm
  weightKg.value = data.weight_kg
  bloodType.value = data.blood_type
  allergies.value = data.allergies
  chronicConditions.value = data.chronic_conditions
  emergencyContactName.value = data.emergency_contact_name
  emergencyContactPhone.value = data.emergency_contact_phone
}

async function loadProfile() {
  loading.value = true
  try {
    const response = await apiClient.get<ProfileData>('/api/profile/')
    populateForm(response.data)
  } catch {
    toast.add({ severity: 'error', summary: 'Помилка', detail: 'Не вдалося завантажити профіль', life: 3000 })
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!dateOfBirth.value) {
    toast.add({ severity: 'warn', summary: 'Увага', detail: 'Дата народження обов\'язкова', life: 3000 })
    return
  }
  saving.value = true
  try {
    const payload = {
      sex: sex.value,
      date_of_birth: formatDateForApi(dateOfBirth.value),
      height_cm: heightCm.value,
      weight_kg: weightKg.value,
      blood_type: bloodType.value,
      allergies: allergies.value || null,
      chronic_conditions: chronicConditions.value || null,
      emergency_contact_name: emergencyContactName.value || null,
      emergency_contact_phone: emergencyContactPhone.value || null,
    }
    const response = await apiClient.put<ProfileData>('/api/profile/', payload)
    populateForm(response.data)
    await auth.fetchUser()
    toast.add({ severity: 'success', summary: 'Збережено', detail: 'Профіль оновлено', life: 3000 })
  } catch {
    toast.add({ severity: 'error', summary: 'Помилка', detail: 'Не вдалося зберегти профіль', life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="profile-page">
    <h1>Профіль</h1>

    <div v-if="loading" class="loading">Завантаження...</div>

    <div v-else class="profile-sections">
      <Card class="section-card">
        <template #title>Демографія</template>
        <template #content>
          <div class="form-grid">
            <div class="field">
              <label>Стать *</label>
              <Select v-model="sex" :options="sexOptions" optionLabel="label" optionValue="value" class="w-full" />
            </div>
            <div class="field">
              <label>Дата народження *</label>
              <DatePicker v-model="dateOfBirth" dateFormat="dd.mm.yy" showIcon class="w-full" />
            </div>
            <div class="field" v-if="calculatedAge !== null">
              <label>Вік</label>
              <div class="age-display">{{ calculatedAge }} р.</div>
            </div>
          </div>
        </template>
      </Card>

      <Card class="section-card">
        <template #title>Фізичні дані</template>
        <template #content>
          <div class="form-grid">
            <div class="field">
              <label>Зріст (см)</label>
              <InputNumber v-model="heightCm" :min="30" :max="250" class="w-full" />
            </div>
            <div class="field">
              <label>Вага (кг)</label>
              <InputNumber v-model="weightKg" :min="1" :max="500" :minFractionDigits="0" :maxFractionDigits="1" class="w-full" />
            </div>
            <div class="field">
              <label>Група крові</label>
              <Select v-model="bloodType" :options="bloodTypeOptions" optionLabel="label" optionValue="value" showClear class="w-full" />
            </div>
          </div>
        </template>
      </Card>

      <Card class="section-card">
        <template #title>Медичні дані</template>
        <template #content>
          <div class="form-grid">
            <div class="field full-width">
              <label>Алергії</label>
              <Textarea v-model="allergies" rows="3" class="w-full" />
            </div>
            <div class="field full-width">
              <label>Хронічні захворювання</label>
              <Textarea v-model="chronicConditions" rows="3" class="w-full" />
            </div>
          </div>
        </template>
      </Card>

      <Card class="section-card">
        <template #title>Екстрений контакт</template>
        <template #content>
          <div class="form-grid">
            <div class="field">
              <label>Ім'я</label>
              <InputText v-model="emergencyContactName" class="w-full" />
            </div>
            <div class="field">
              <label>Телефон</label>
              <InputText v-model="emergencyContactPhone" class="w-full" />
            </div>
          </div>
        </template>
      </Card>

      <div class="actions">
        <Button label="Зберегти" icon="pi pi-check" :loading="saving" @click="saveProfile" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 800px;
}
.profile-page h1 {
  font-size: 1.5rem;
  font-weight: 300;
  color: #e4e4e7;
  margin-bottom: 1.5rem;
  letter-spacing: 0.02em;
}
.loading {
  color: #71717a;
  font-size: 0.875rem;
}
.profile-sections {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.section-card {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.section-card :deep(.p-card-title) {
  font-size: 0.75rem;
  font-weight: 600;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.section-card :deep(.p-card-body) {
  background: transparent;
}
.section-card :deep(.p-card-content) {
  background: transparent;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.field label {
  font-size: 0.75rem;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.field.full-width {
  grid-column: 1 / -1;
}
.w-full {
  width: 100%;
}
.age-display {
  font-size: 1.25rem;
  font-weight: 300;
  color: #e4e4e7;
  padding: 0.5rem 0;
}
.actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>

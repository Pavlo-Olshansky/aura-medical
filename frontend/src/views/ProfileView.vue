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
import ToggleSwitch from 'primevue/toggleswitch'
import { apiClient } from '@/api/client'
import { usePushNotifications } from '@/composables/usePushNotifications'
import PushSetupGuide from '@/components/PushSetupGuide.vue'
import { useAuthStore, isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import type { ProfileData } from '@/types'
import { formatDateForApi } from '@/utils/dateUtils'
import { useEnterSubmit } from '@/composables/useEnterSubmit'

const toast = useToast()
const auth = useAuthStore()

const loading = ref(true)
const { isSupported: pushSupported, isSubscribed: pushSubscribed, permissionState: pushPermission, checkSubscription, subscribe: pushSubscribe, unsubscribe: pushUnsubscribe } = usePushNotifications()
const pushToggleLoading = ref(false)

async function togglePush(val: boolean) {
  pushToggleLoading.value = true
  if (val) {
    await pushSubscribe()
  } else {
    await pushUnsubscribe()
  }
  await checkSubscription()
  pushToggleLoading.value = false
}
const saving = ref(false)
const textareaFocused = ref(false)

useEnterSubmit(saveProfile)

const sex = ref<string>('male')
const dateOfBirth = ref<Date | null>(null)
const heightCm = ref<number | null>(null)
const weightKg = ref<number | null>(null)
const bloodType = ref<string | null>(null)
const allergies = ref<string | null>(null)
const chronicConditions = ref<string | null>(null)
const emergencyContactName = ref<string | null>(null)
const emergencyContactPhone = ref<string | null>(null)
const weatherCity = ref<string | null>(null)
const weatherCityAuto = ref(true)
const detecting = ref(false)

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
  weatherCity.value = data.weather_city
  weatherCityAuto.value = data.weather_city_auto
}

async function loadProfile() {
  if (isDemoMode.value) {
    populateForm(demo().getProfile())
    loading.value = false
    return
  }
  loading.value = true
  try {
    const response = await apiClient.get<ProfileData>('/api/v1/profile/')
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
  if (isDemoMode.value) {
    toast.add({ severity: 'info', summary: 'Збережено', detail: 'Збережено в демо-режимі (тимчасово)', life: 3000 })
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
      weather_city: weatherCity.value || null,
      weather_city_auto: weatherCityAuto.value,
    }
    const response = await apiClient.put<ProfileData>('/api/v1/profile/', payload)
    populateForm(response.data)
    await auth.fetchUser()
    toast.add({ severity: 'success', summary: 'Збережено', detail: 'Профіль оновлено', life: 3000 })
  } catch {
    toast.add({ severity: 'error', summary: 'Помилка', detail: 'Не вдалося зберегти профіль', life: 3000 })
  } finally {
    saving.value = false
  }
}

async function detectCity() {
  if (isDemoMode.value) {
    weatherCity.value = 'Київ'
    toast.add({ severity: 'success', summary: 'Визначено', detail: 'Місто: Київ (демо)', life: 3000 })
    return
  }
  detecting.value = true
  try {
    const response = await apiClient.post<{ city: string | null; saved: boolean }>('/api/v1/weather/detect-city')
    if (response.data.city) {
      weatherCity.value = response.data.city
      toast.add({ severity: 'success', summary: 'Визначено', detail: `Місто: ${response.data.city}`, life: 3000 })
    } else {
      toast.add({ severity: 'warn', summary: 'Увага', detail: 'Не вдалося визначити місто', life: 3000 })
    }
  } catch {
    toast.add({ severity: 'error', summary: 'Помилка', detail: 'Не вдалося визначити місто', life: 3000 })
  } finally {
    detecting.value = false
  }
}

onMounted(() => {
  loadProfile()
  checkSubscription()
})
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
              <Textarea
                v-model="allergies"
                rows="3"
                class="w-full"
                @focus="textareaFocused = true"
                @blur="textareaFocused = false"
                @keydown.ctrl.enter.prevent="saveProfile"
                @keydown.meta.enter.prevent="saveProfile"
              />
            </div>
            <div class="field full-width">
              <label>Хронічні захворювання</label>
              <Textarea
                v-model="chronicConditions"
                rows="3"
                class="w-full"
                @focus="textareaFocused = true"
                @blur="textareaFocused = false"
                @keydown.ctrl.enter.prevent="saveProfile"
                @keydown.meta.enter.prevent="saveProfile"
              />
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

      <Card class="section-card">
        <template #title>Погода</template>
        <template #content>
          <div class="form-grid">
            <div class="field">
              <label>Місто для прогнозу</label>
              <div class="city-input-row">
                <InputText v-model="weatherCity" class="w-full" placeholder="напр. Kyiv" />
                <Button
                  icon="pi pi-map-marker"
                  severity="secondary"
                  outlined
                  :loading="detecting"
                  @click="detectCity"
                  v-tooltip.top="'Визначити місто за IP-адресою'"
                />
              </div>
            </div>
            <div class="field">
              <label>Автовизначення</label>
              <div class="toggle-row">
                <ToggleSwitch v-model="weatherCityAuto" />
                <span class="toggle-hint">{{ weatherCityAuto ? 'Місто визначається автоматично при першому вході' : 'Місто встановлено вручну' }}</span>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <Card v-if="pushSupported" class="section-card">
        <template #title>Сповіщення</template>
        <template #content>
          <div class="field">
            <div class="toggle-row">
              <ToggleSwitch
                :modelValue="pushSubscribed"
                @update:modelValue="togglePush"
                :disabled="pushToggleLoading || pushPermission === 'denied'"
              />
              <span v-if="pushPermission === 'denied'" class="toggle-hint" style="color: var(--danger)">
                Заблоковано браузером. Дозвольте сповіщення в налаштуваннях браузера.
              </span>
              <span v-else class="toggle-hint">
                {{ pushSubscribed ? 'Push-нагадування увімкнено' : 'Push-нагадування вимкнено' }}
              </span>
            </div>
          </div>
          <PushSetupGuide />
        </template>
      </Card>

      <div class="actions">
        <Button :label="textareaFocused ? 'Зберегти (Ctrl+Enter)' : 'Зберегти'" icon="pi pi-check" :loading="saving" @click="saveProfile" />
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
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  letter-spacing: 0.02em;
}
.loading {
  color: var(--text-muted);
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
  border: 1px solid var(--border-subtle);
}
.section-card :deep(.p-card-title) {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-faint);
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
  color: var(--text-muted);
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
  color: var(--text-primary);
  padding: 0.5rem 0;
}
.city-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}
.toggle-hint {
  font-size: 0.75rem;
  color: var(--text-faint);
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

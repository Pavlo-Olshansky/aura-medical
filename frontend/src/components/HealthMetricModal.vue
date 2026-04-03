<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { useHealthMetricsStore } from '@/stores/healthMetrics'
import type { MetricType } from '@/types'
import { formatDateTimeForApi } from '@/utils/dateUtils'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: []
}>()

const toast = useToast()
const healthMetricsStore = useHealthMetricsStore()

const selectedMetricType = ref<MetricType | null>(null)
const value = ref<number | null>(null)
const secondaryValue = ref<number | null>(null)
const date = ref<Date>(new Date())
const notes = ref('')
const saving = ref(false)

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val),
})

const showSecondary = computed(() => selectedMetricType.value?.has_secondary_value ?? false)

const unitLabel = computed(() => selectedMetricType.value?.unit || '')

watch(() => props.visible, async (val) => {
  if (val) {
    if (healthMetricsStore.metricTypes.length === 0) {
      await healthMetricsStore.fetchMetricTypes()
    }
    resetForm()
  }
})

function resetForm() {
  selectedMetricType.value = null
  value.value = null
  secondaryValue.value = null
  date.value = new Date()
  notes.value = ''
}

async function handleSave() {
  if (!selectedMetricType.value || value.value == null) return

  saving.value = true
  try {
    const payload: Record<string, unknown> = {
      metric_type_id: selectedMetricType.value.id,
      value: value.value,
      date: formatDateTimeForApi(date.value),
      notes: notes.value || null,
    }
    if (showSecondary.value && secondaryValue.value != null) {
      payload.secondary_value = secondaryValue.value
    }

    await healthMetricsStore.createHealthMetric(payload)

    toast.add({
      severity: 'success',
      summary: 'Збережено',
      detail: 'Показник успішно додано',
      life: 3000,
    })

    emit('update:visible', false)
    emit('saved')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    toast.add({
      severity: 'error',
      summary: 'Помилка',
      detail: err.response?.data?.detail || 'Не вдалося зберегти показник',
      life: 5000,
    })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    header="Додати показник здоров'я"
    modal
    dismissableMask
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
  >
    <div class="modal-form">
      <div class="form-field">
        <label>Тип показника *</label>
        <Dropdown
          v-model="selectedMetricType"
          :options="healthMetricsStore.metricTypes"
          optionLabel="name"
          placeholder="Оберіть тип"
          class="w-full"
        />
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>Значення * <span v-if="unitLabel" class="unit-hint">({{ unitLabel }})</span></label>
          <InputNumber v-model="value" :minFractionDigits="0" :maxFractionDigits="2" placeholder="0" />
        </div>

        <div v-if="showSecondary" class="form-field">
          <label>Діастолічний <span v-if="unitLabel" class="unit-hint">({{ unitLabel }})</span></label>
          <InputNumber v-model="secondaryValue" :minFractionDigits="0" :maxFractionDigits="2" placeholder="0" />
        </div>
      </div>

      <div class="form-field">
        <label>Дата та час</label>
        <Calendar
          v-model="date"
          dateFormat="dd.mm.yy"
          showTime
          hourFormat="24"
          showIcon
          placeholder="Оберіть дату"
        />
      </div>

      <div class="form-field">
        <label>Примітки</label>
        <Textarea v-model="notes" rows="3" placeholder="Необов'язково" />
      </div>
    </div>

    <template #footer>
      <Button label="Скасувати" severity="secondary" text @click="dialogVisible = false" />
      <Button
        label="Зберегти"
        icon="pi pi-check"
        :loading="saving"
        :disabled="!selectedMetricType || value == null"
        @click="handleSave"
      />
    </template>
  </Dialog>
</template>

<style scoped>
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #a1a1aa;
}
.form-row {
  display: flex;
  gap: 1rem;
}
.form-row .form-field {
  flex: 1;
}
.unit-hint {
  color: #71717a;
  font-weight: 400;
}
.w-full {
  width: 100%;
}
</style>

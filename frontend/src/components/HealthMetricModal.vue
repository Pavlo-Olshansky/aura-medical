<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue'
import Dialog from 'primevue/dialog'
import AppConfirmDialog from '@/components/AppConfirmDialog.vue'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { useHealthMetricsStore } from '@/stores/healthMetrics'
import { useFormDirtyCheck } from '@/composables/useFormDirtyCheck'
import { useEnterSubmit } from '@/composables/useEnterSubmit'
import type { MetricType, HealthMetric } from '@/types'
import { formatDateTimeForApi } from '@/utils/dateUtils'

const props = defineProps<{
  visible: boolean
  preselectedType?: MetricType | null
  editMetric?: HealthMetric | null
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

const isEdit = computed(() => !!props.editMetric)
const dialogTitle = computed(() => isEdit.value ? 'Редагувати показник' : "Додати показник здоров'я")

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val),
})

const textareaFocused = ref(false)

const { capture, confirmDiscard, setupEscapeHandler } = useFormDirtyCheck(() => ({
  selectedMetricType: selectedMetricType.value?.id ?? null,
  value: value.value,
  secondaryValue: secondaryValue.value,
  notes: notes.value,
}))

const visibleRef = computed(() => props.visible)
setupEscapeHandler(visibleRef, () => emit('update:visible', false))
useEnterSubmit(handleSave, visibleRef)

const showSecondary = computed(() => selectedMetricType.value?.has_secondary_value ?? false)

const unitLabel = computed(() => selectedMetricType.value?.unit || '')

watch(() => props.visible, async (val) => {
  if (val) {
    if (healthMetricsStore.metricTypes.length === 0) {
      await healthMetricsStore.fetchMetricTypes()
    }
    resetForm()
    nextTick(() => capture())
  }
})

function resetForm() {
  if (props.editMetric) {
    selectedMetricType.value = healthMetricsStore.metricTypes.find(
      (t) => t.id === props.editMetric!.metric_type_id,
    ) ?? props.editMetric.metric_type ?? null
    value.value = props.editMetric.value
    secondaryValue.value = props.editMetric.secondary_value ?? null
    date.value = new Date(props.editMetric.date)
    notes.value = props.editMetric.notes || ''
  } else {
    selectedMetricType.value = props.preselectedType ?? null
    value.value = null
    secondaryValue.value = null
    date.value = new Date()
    notes.value = ''
  }
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

    if (isEdit.value && props.editMetric) {
      await healthMetricsStore.updateHealthMetric(props.editMetric.id, payload)
    } else {
      await healthMetricsStore.createHealthMetric(payload)
    }

    toast.add({
      severity: 'success',
      summary: 'Збережено',
      detail: isEdit.value ? 'Показник успішно оновлено' : 'Показник успішно додано',
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
  <AppConfirmDialog />
  <Dialog
    v-model:visible="dialogVisible"
    :header="dialogTitle"
    modal
    dismissableMask
    :closeOnEscape="false"
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
  >
    <form id="healthMetricForm" class="modal-form" @submit.prevent="handleSave">
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
        <Textarea
          v-model="notes"
          rows="3"
          placeholder="Необов'язково"
          @focus="textareaFocused = true"
          @blur="textareaFocused = false"
          @keydown.ctrl.enter.prevent="handleSave"
          @keydown.meta.enter.prevent="handleSave"
        />
      </div>
    </form>

    <template #footer>
      <Button label="Скасувати" severity="secondary" text @click="dialogVisible = false" />
      <Button
        :label="textareaFocused ? 'Зберегти (Ctrl+Enter)' : 'Зберегти'"
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

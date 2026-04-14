<script setup lang="ts">
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import AutoComplete from 'primevue/autocomplete'
import type { AutoCompleteOptionSelectEvent } from 'primevue/autocomplete'
import Button from 'primevue/button'
import type { BiomarkerReference } from '@/types'

export interface EntryData {
  biomarkerName: string
  value: number | null
  unit: string
  ref_min: number | null
  ref_max: number | null
}

const props = defineProps<{
  entry: EntryData
  index: number
  biomarkerSuggestions: BiomarkerReference[]
  canRemove: boolean
}>()

const emit = defineEmits<{
  (e: 'update', index: number, field: keyof EntryData, value: string | number | null): void
  (e: 'remove', index: number): void
  (e: 'biomarkerSearch', query: string): void
  (e: 'biomarkerSelect', index: number, biomarker: BiomarkerReference): void
}>()

function onFieldUpdate(field: keyof EntryData, value: string | number | null) {
  emit('update', props.index, field, value)
}

function onBiomarkerSearch(event: { query: string }) {
  emit('biomarkerSearch', event.query)
}

function onBiomarkerSelect(event: AutoCompleteOptionSelectEvent) {
  emit('biomarkerSelect', props.index, event.value)
}
</script>

<template>
  <div class="entry-row">
    <div class="entry-field entry-biomarker">
      <label>Біомаркер</label>
      <AutoComplete
        :modelValue="entry.biomarkerName"
        @update:modelValue="onFieldUpdate('biomarkerName', $event)"
        :suggestions="biomarkerSuggestions"
        optionLabel="name"
        placeholder="Назва біомаркера"
        @complete="onBiomarkerSearch"
        @item-select="onBiomarkerSelect"
        :forceSelection="false"
      />
    </div>
    <div class="entry-field entry-value">
      <label>Значення</label>
      <InputNumber
        :modelValue="entry.value"
        @update:modelValue="onFieldUpdate('value', $event)"
        :minFractionDigits="0"
        :maxFractionDigits="4"
        placeholder="0"
      />
    </div>
    <div class="entry-field entry-unit">
      <label>Одиниця</label>
      <InputText
        :modelValue="entry.unit"
        @update:modelValue="onFieldUpdate('unit', $event ?? '')"
        placeholder="од."
      />
    </div>
    <div class="entry-field entry-ref">
      <label>Мін</label>
      <InputNumber
        :modelValue="entry.ref_min"
        @update:modelValue="onFieldUpdate('ref_min', $event)"
        :minFractionDigits="0"
        :maxFractionDigits="4"
        placeholder="-"
      />
    </div>
    <div class="entry-field entry-ref">
      <label>Макс</label>
      <InputNumber
        :modelValue="entry.ref_max"
        @update:modelValue="onFieldUpdate('ref_max', $event)"
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
        @click="emit('remove', index)"
        :disabled="!canRemove"
      />
    </div>
  </div>
</template>

<style scoped>
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

@media (max-width: 768px) {
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

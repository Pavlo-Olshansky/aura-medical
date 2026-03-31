<script setup lang="ts">
import { DENSITY_COLORS, ACTIVE_TREATMENT_STROKE } from './body-regions'

defineProps<{
  unmappedCount: number
  wholeBodyCount: number
}>()

defineEmits<{
  (e: 'click-unmapped'): void
  (e: 'click-whole-body'): void
}>()

const legendItems = [
  { color: DENSITY_COLORS[0], label: 'Немає даних' },
  { color: DENSITY_COLORS[1], label: '1-2 візити' },
  { color: DENSITY_COLORS[3], label: '3-5 візитів' },
  { color: DENSITY_COLORS[6], label: '6-10 візитів' },
  { color: DENSITY_COLORS[11], label: '11+ візитів' },
]
</script>

<template>
  <div class="body-map-legend">
    <div class="color-legend">
      <div v-for="item in legendItems" :key="item.color" class="legend-item">
        <span class="legend-swatch" :style="{ background: item.color }" />
        <span class="legend-label">{{ item.label }}</span>
      </div>
      <div class="legend-item">
        <span class="legend-swatch treatment-swatch" />
        <span class="legend-label">Активне лікування</span>
      </div>
    </div>

    <div class="badges">
      <button
        v-if="unmappedCount > 0"
        class="badge"
        @click="$emit('click-unmapped')"
      >
        {{ unmappedCount }} візитів без прив'язки
      </button>
      <button
        v-if="wholeBodyCount > 0"
        class="badge"
        @click="$emit('click-whole-body')"
      >
        {{ wholeBodyCount }} загальних візитів (все тіло)
      </button>
    </div>
  </div>
</template>

<style scoped>
.body-map-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}
.color-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.legend-swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  flex-shrink: 0;
  box-shadow: 0 0 4px currentColor;
}
.treatment-swatch {
  background: #E8E8E8;
  border: 2px solid v-bind('ACTIVE_TREATMENT_STROKE');
  box-shadow: 0 0 4px v-bind('ACTIVE_TREATMENT_STROKE');
}
.legend-label {
  font-size: 0.75rem;
  color: #94a3b8;
}
.badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.badge {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #334155;
  border-radius: 1rem;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
  cursor: pointer;
  transition: background 0.15s;
}
.badge:hover {
  background: #334155;
  color: #e2e8f0;
}
</style>

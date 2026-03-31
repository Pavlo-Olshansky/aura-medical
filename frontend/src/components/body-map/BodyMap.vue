<script setup lang="ts">
import { ref, computed } from 'vue'
import type { BodyMapView, BodyRegionKey, BodyRegionSummary } from './types'
import { FRONT_POLYGONS } from './body-data-front'
import { BACK_POLYGONS } from './body-data-back'
import {
  BODY_REGION_LABELS,
  getDensityColor,
  ACTIVE_TREATMENT_STROKE,
  SELECTED_STROKE,
} from './body-regions'
import BodyMapTooltip from './BodyMapTooltip.vue'

const props = defineProps<{
  regions: Record<string, BodyRegionSummary>
  selectedRegion: BodyRegionKey | null
}>()

const emit = defineEmits<{
  (e: 'select', region: BodyRegionKey | null): void
}>()

const view = ref<BodyMapView>('front')
const hoveredRegion = ref<BodyRegionKey | null>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)

const polygons = computed(() => view.value === 'front' ? FRONT_POLYGONS : BACK_POLYGONS)

function getRegionData(key: string): BodyRegionSummary {
  return props.regions[key] || { visit_count: 0, active_treatment_count: 0, last_visit_date: null, visits_last_year: 0 }
}

function getFill(region: BodyRegionKey): string {
  return getDensityColor(getRegionData(region).visit_count)
}

function getStroke(region: BodyRegionKey): string {
  if (props.selectedRegion === region) return SELECTED_STROKE
  if (getRegionData(region).active_treatment_count > 0) return ACTIVE_TREATMENT_STROKE
  return 'none'
}

function getStrokeWidth(region: BodyRegionKey): number {
  if (props.selectedRegion === region) return 2
  if (getRegionData(region).active_treatment_count > 0) return 2
  return 0
}

function onMouseEnter(region: BodyRegionKey, event: MouseEvent) {
  hoveredRegion.value = region
  tooltipX.value = event.clientX
  tooltipY.value = event.clientY
}

function onMouseMove(event: MouseEvent) {
  tooltipX.value = event.clientX
  tooltipY.value = event.clientY
}

function onMouseLeave() {
  hoveredRegion.value = null
}

function onClick(region: BodyRegionKey) {
  emit('select', props.selectedRegion === region ? null : region)
}

function onKeydown(region: BodyRegionKey, event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    onClick(region)
  }
}

const hasAnyData = computed(() => Object.keys(props.regions).length > 0)

const tooltipData = computed(() => {
  if (!hoveredRegion.value) return null
  const data = getRegionData(hoveredRegion.value)
  return {
    label: BODY_REGION_LABELS[hoveredRegion.value] || hoveredRegion.value,
    visitCount: data.visit_count,
    treatmentCount: data.active_treatment_count,
  }
})
</script>

<template>
  <div class="body-map-container">
    <div class="view-toggle">
      <button
        :class="['toggle-btn', { active: view === 'front' }]"
        @click="view = 'front'"
      >
        Спереду
      </button>
      <button
        :class="['toggle-btn', { active: view === 'back' }]"
        @click="view = 'back'"
      >
        Ззаду
      </button>
    </div>

    <svg
      viewBox="0 0 200 390"
      class="body-svg"
      @mousemove="onMouseMove"
    >
      <polygon
        v-for="poly in polygons"
        :key="poly.region + '-' + view"
        :points="poly.points"
        :fill="getFill(poly.region)"
        :stroke="getStroke(poly.region)"
        :stroke-width="getStrokeWidth(poly.region)"
        :class="['body-region', { hovered: hoveredRegion === poly.region, selected: selectedRegion === poly.region }]"
        role="button"
        :tabindex="0"
        :aria-label="BODY_REGION_LABELS[poly.region] || poly.region"
        @mouseenter="onMouseEnter(poly.region, $event)"
        @mouseleave="onMouseLeave"
        @click="onClick(poly.region)"
        @keydown="onKeydown(poly.region, $event)"
      />
    </svg>

    <p v-if="!hasAnyData" class="empty-message">
      Додайте ділянку тіла до візитів, щоб побачити карту
    </p>

    <Teleport to="body">
      <BodyMapTooltip
        v-if="tooltipData"
        :label="tooltipData.label"
        :visit-count="tooltipData.visitCount"
        :treatment-count="tooltipData.treatmentCount"
        :x="tooltipX"
        :y="tooltipY"
      />
    </Teleport>
  </div>
</template>

<style scoped>
.body-map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.view-toggle {
  display: flex;
  gap: 0;
  margin-bottom: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
}
.toggle-btn {
  padding: 0.375rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  background: #fff;
  border: none;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}
.toggle-btn.active {
  background: #2563eb;
  color: #fff;
}
.toggle-btn:not(.active):hover {
  background: #f1f5f9;
}
.body-svg {
  width: 100%;
  max-width: 240px;
  height: auto;
}
.body-region {
  cursor: pointer;
  transition: fill 0.2s ease, stroke 0.2s ease, filter 0.2s ease;
  outline: none;
}
.body-region.hovered {
  filter: brightness(1.15);
}
.body-region.selected {
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.6));
}
.body-region:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 1px;
}
.empty-message {
  font-size: 0.8125rem;
  color: #94a3b8;
  text-align: center;
  margin-top: 0.5rem;
}
</style>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { BodyRegionKey, BodyRegionSummary, PolygonData } from './types'
import { FRONT_POLYGONS } from './body-data-front'
import { BACK_POLYGONS } from './body-data-back'
import { FACE_POLYGONS } from './body-data-face'
import {
  BODY_REGION_LABELS,
  getDensityColor,
} from './body-regions'
import BodyMapTooltip from './BodyMapTooltip.vue'

import bodyImage from '@/assets/body/body-image.jpg'

// Full image: 1400x763
const VIEW_BOX = '0 0 1400 763'

const allPolygons: PolygonData[] = [...FRONT_POLYGONS, ...BACK_POLYGONS, ...FACE_POLYGONS]

const props = defineProps<{
  regions: Record<string, BodyRegionSummary>
  selectedRegion: BodyRegionKey | null
}>()

const emit = defineEmits<{
  (e: 'select', region: BodyRegionKey | null): void
}>()

const hoveredRegion = ref<BodyRegionKey | null>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)
const imageError = ref(false)

function getRegionData(key: string): BodyRegionSummary {
  return props.regions[key] || { visit_count: 0, active_treatment_count: 0, last_visit_date: null, visits_last_year: 0 }
}

function regionClasses(region: BodyRegionKey) {
  return {
    'click-region': true,
    hovered: hoveredRegion.value === region,
    selected: props.selectedRegion === region,
    'has-treatment': getRegionData(region).active_treatment_count > 0,
  }
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

const visibleDots = computed(() =>
  allPolygons.filter(p => getRegionData(p.region).visit_count > 0)
)

function dotStyle(poly: PolygonData) {
  const data = getRegionData(poly.region)
  const color = getDensityColor(data.visit_count)
  const pctX = (poly.centerX / 1400) * 100
  const pctY = (poly.centerY / 763) * 100
  return {
    left: `${pctX}%`,
    top: `${pctY}%`,
    background: color,
    boxShadow: `0 0 6px ${color}`,
  }
}
</script>

<template>
  <div class="body-map-container" @mousemove="onMouseMove">
    <div class="body-map-image-wrap">
      <img
        v-if="!imageError"
        :src="bodyImage"
        class="body-map-img"
        alt=""
        @error="imageError = true"
      />
      <div v-else class="body-map-fallback">
        <i class="pi pi-image" />
      </div>

      <svg :viewBox="VIEW_BOX" class="body-map-svg" @mouseleave="onMouseLeave">
        <polygon
          v-for="poly in allPolygons"
          :key="poly.region + '-' + poly.centerX"
          :points="poly.points"
          :class="regionClasses(poly.region)"
          role="button"
          :tabindex="0"
          :aria-label="BODY_REGION_LABELS[poly.region] || poly.region"
          @mouseenter="onMouseEnter(poly.region, $event)"
          @click="onClick(poly.region)"
          @keydown="onKeydown(poly.region, $event)"
        />
      </svg>

      <div
        v-for="poly in visibleDots"
        :key="poly.region + '-dot-' + poly.centerX"
        class="density-dot"
        :style="dotStyle(poly)"
      />
    </div>

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
  width: 100%;
}

.body-map-image-wrap {
  position: relative;
  width: 100%;
}

.body-map-img {
  display: block;
  width: 100%;
  height: auto;
}

.body-map-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1400 / 763;
  background: #0a0a0a;
  color: #334155;
  font-size: 2rem;
}

.body-map-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.click-region {
  fill: transparent;
  stroke: transparent;
  stroke-width: 0;
  cursor: pointer;
  pointer-events: all;
  transition: fill 0.3s, stroke 0.3s;
}

.click-region.hovered {
  fill: rgba(0, 240, 255, 0.1);
  stroke: rgba(0, 240, 255, 0.4);
  stroke-width: 2;
}

.click-region.selected {
  fill: rgba(0, 240, 255, 0.15);
  stroke: rgba(0, 240, 255, 0.8);
  stroke-width: 2.5;
}

.click-region.has-treatment {
  stroke: #F59E0B;
  stroke-width: 2;
}

.click-region.selected.has-treatment {
  stroke: rgba(0, 240, 255, 0.8);
}

.click-region:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

.density-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 5;
}

.empty-message {
  font-size: 0.8125rem;
  color: #3f3f46;
  text-align: center;
  margin-top: 0.5rem;
}
</style>

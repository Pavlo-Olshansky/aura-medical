<script setup lang="ts">
import { ref, computed } from 'vue'
import type { BodyRegionKey, BodyRegionSummary, HotspotData } from './types'
import {
  BODY_REGION_LABELS,
  getDensityColor,
} from './body-regions'
import BodyMapTooltip from './BodyMapTooltip.vue'

import frontMaleImage from '@/assets/body/front.jpg'
import backMaleImage from '@/assets/body/back.jpg'
import faceMaleImage from '@/assets/body/face.jpg'
import frontFemaleImage from '@/assets/body/front-woman.png'
import backFemaleImage from '@/assets/body/back-woman.png'
import faceFemaleImage from '@/assets/body/face-woman.png'

// --- Hotspot coordinate data (% relative to each panel viewport after object-fit:cover) ---

const FRONT_HOTSPOTS: HotspotData[] = [
  { region: 'neck_throat',    top: '16%',  left: '47%',  width: '14%',  height: '5%' },
  { region: 'shoulder_left',  top: '18%',  left: '30%',  width: '16%',  height: '8%' },
  { region: 'shoulder_right', top: '18%',  left: '62%',  width: '16%',  height: '8%' },
  { region: 'chest',          top: '20%',  left: '41%',  width: '28%',  height: '13%' },
  { region: 'arm_left',       top: '26%',  left: '27%',  width: '14%',  height: '21%' },
  { region: 'arm_right',      top: '26%',  left: '67%',  width: '14%',  height: '21%' },
  { region: 'hand_left',      top: '48%',  left: '25%',  width: '12%',  height: '9%' },
  { region: 'hand_right',     top: '48%',  left: '71%',  width: '12%',  height: '9%' },
  { region: 'abdomen_upper',  top: '33%',  left: '42%',  width: '26%',  height: '10%' },
  { region: 'pelvis',         top: '42%',  left: '40%',  width: '30%',  height: '9%' },
  { region: 'leg_left',       top: '52%',  left: '39%',  width: '15%',  height: '31%' },
  { region: 'leg_right',      top: '52%',  left: '55%',  width: '15%',  height: '31%' },
  { region: 'foot_left',      top: '84%',  left: '36%',  width: '16%',  height: '5%' },
  { region: 'foot_right',     top: '84%',  left: '58%',  width: '16%',  height: '5%' },
]

const BACK_HOTSPOTS: HotspotData[] = [
  { region: 'shoulder_left',  top: '16%',  left: '25%',  width: '17%',  height: '8%' },
  { region: 'shoulder_right', top: '16%',  left: '60%',  width: '17%',  height: '8%' },
  { region: 'back_upper',     top: '20%',  left: '30%',  width: '40%',  height: '16%' },
  { region: 'back_lower',     top: '36%',  left: '34%',  width: '32%',  height: '15%' },
  { region: 'leg_left',       top: '53%',  left: '34%',  width: '16%',  height: '33%' },
  { region: 'leg_right',      top: '53%',  left: '52%',  width: '16%',  height: '33%' },
  { region: 'foot_left',      top: '87%',  left: '33%',  width: '17%',  height: '5%' },
  { region: 'foot_right',     top: '87%',  left: '53%',  width: '18%',  height: '5%' },
]

const FACE_HOTSPOTS: HotspotData[] = [
  { region: 'head_cranium',  top: '0%',   left: '10%',  width: '80%',  height: '28%' },
  { region: 'head_face',     top: '26%',  left: '12%',  width: '76%',  height: '46%' },
  { region: 'eyes',          top: '40%',  left: '18%',  width: '64%',  height: '9%' },
  { region: 'ears',          top: '42%',  left: '2%',   width: '12%',  height: '19%' },
  { region: 'ears',          top: '42%',  left: '86%',  width: '12%',  height: '19%' },
  { region: 'nose',          top: '43%',  left: '39%',  width: '20%',  height: '19%' },
  { region: 'mouth_teeth',   top: '63%',  left: '25%',  width: '46%',  height: '10%' },
]

const props = defineProps<{
  regions: Record<string, BodyRegionSummary>
  selectedRegion: BodyRegionKey | null
  sex?: string
}>()

const panels = computed(() => {
  const isFemale = props.sex === 'female'
  return [
    { key: 'front' as const, label: 'Спереду', image: isFemale ? frontFemaleImage : frontMaleImage, hotspots: FRONT_HOTSPOTS },
    { key: 'back' as const, label: 'Ззаду', image: isFemale ? backFemaleImage : backMaleImage, hotspots: BACK_HOTSPOTS },
    { key: 'face' as const, label: 'Обличчя', image: isFemale ? faceFemaleImage : faceMaleImage, hotspots: FACE_HOTSPOTS },
  ]
})

const emit = defineEmits<{
  (e: 'select', region: BodyRegionKey | null): void
}>()

const hoveredRegion = ref<BodyRegionKey | null>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)
const imageErrors = ref<Record<string, boolean>>({})

function getRegionData(key: string): BodyRegionSummary {
  return props.regions[key] || { visit_count: 0, active_treatment_count: 0, last_visit_date: null, visits_last_year: 0 }
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

function hotspotClasses(region: BodyRegionKey) {
  const data = getRegionData(region)
  return {
    hotspot: true,
    hovered: hoveredRegion.value === region,
    selected: props.selectedRegion === region,
    'has-treatment': data.active_treatment_count > 0,
    'has-visits': data.visit_count > 0,
  }
}

function hotspotStyle(hs: HotspotData) {
  const data = getRegionData(hs.region)
  const style: Record<string, string> = {
    top: hs.top,
    left: hs.left,
    width: hs.width,
    height: hs.height,
  }
  if (data.visit_count > 0) {
    const color = getDensityColor(data.visit_count)
    style.borderColor = color
    style.boxShadow = `inset 0 0 8px ${color}40`
  }
  return style
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
  <div class="body-map-container" @mousemove="onMouseMove">
    <div class="panels">
      <div
        v-for="panel in panels"
        :key="panel.key"
        class="panel"
      >
        <div class="panel-viewport">
          <img
            v-if="!imageErrors[panel.key]"
            :src="panel.image"
            class="panel-img"
            alt=""
            @error="imageErrors[panel.key] = true"
          />
          <div v-else class="panel-fallback">
            <i class="pi pi-image" />
          </div>

          <button
            v-for="(hs, idx) in panel.hotspots"
            :key="`${panel.key}-${idx}`"
            :class="hotspotClasses(hs.region)"
            :style="hotspotStyle(hs)"
            :aria-label="BODY_REGION_LABELS[hs.region] || hs.region"
            @mouseenter="onMouseEnter(hs.region, $event)"
            @mouseleave="onMouseLeave"
            @click="onClick(hs.region)"
            @keydown="onKeydown(hs.region, $event)"
          />
        </div>
        <div class="panel-label">{{ panel.label }}</div>
      </div>
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

.panels {
  display: flex;
  width: 100%;
  gap: 4px;
  align-items: flex-start;
}

.panel {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.panel-viewport {
  position: relative;
  overflow: hidden;
  width: 100%;
  aspect-ratio: 3 / 5;
  border-radius: 4px;
}

.panel-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.panel-label {
  font-size: 0.6875rem;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 4px;
  text-align: center;
}

.panel-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #0a0a0a;
  color: #334155;
  font-size: 2rem;
}

.hotspot {
  position: absolute;
  border: 1px dashed rgba(0, 240, 255, 0.25);
  background: transparent;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0;
  outline: none;
}

.hotspot:hover,
.hotspot.hovered {
  background: rgba(0, 240, 255, 0.05);
  border-color: rgba(0, 240, 255, 0.4);
}

.hotspot.selected {
  background: rgba(0, 240, 255, 0.12);
  border-color: rgba(0, 240, 255, 0.7);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
}

.hotspot.has-treatment {
  border-color: #F59E0B;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
}

.hotspot.selected.has-treatment {
  border-color: rgba(0, 240, 255, 0.7);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
}

.hotspot:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 1px;
}

.empty-message {
  font-size: 0.8125rem;
  color: #3f3f46;
  text-align: center;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .panels {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .panel {
    width: 95%;
  }
}
</style>

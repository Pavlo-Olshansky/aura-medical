<script setup lang="ts">
import { ref, computed } from 'vue'
import type { BodyRegionKey, BodyRegionSummary, HotspotData } from './types'
import {
  BODY_REGION_LABELS,
  getDensityColor,
} from './body-regions'
import BodyMapTooltip from './BodyMapTooltip.vue'

import bodyImage from '@/assets/body/body-image.jpg'

// --- Hotspot coordinate data (% relative to each panel) ---

const FRONT_HOTSPOTS: HotspotData[] = [
  { region: 'neck_throat', top: '16%', left: '38%', width: '24%', height: '5%' },
  { region: 'shoulder_left', top: '20%', left: '15%', width: '18%', height: '10%' },
  { region: 'shoulder_right', top: '20%', left: '67%', width: '18%', height: '10%' },
  { region: 'chest', top: '25%', left: '22%', width: '56%', height: '16%' },
  { region: 'arm_left', top: '22%', left: '4%', width: '16%', height: '38%' },
  { region: 'arm_right', top: '22%', left: '80%', width: '16%', height: '38%' },
  { region: 'hand_left', top: '55%', left: '0%', width: '14%', height: '12%' },
  { region: 'hand_right', top: '55%', left: '86%', width: '14%', height: '12%' },
  { region: 'abdomen_upper', top: '41%', left: '28%', width: '44%', height: '10%' },
  { region: 'abdomen_lower', top: '51%', left: '30%', width: '40%', height: '10%' },
  { region: 'pelvis', top: '61%', left: '28%', width: '44%', height: '9%' },
  { region: 'leg_left', top: '70%', left: '22%', width: '24%', height: '24%' },
  { region: 'leg_right', top: '70%', left: '54%', width: '24%', height: '24%' },
  { region: 'foot_left', top: '92%', left: '22%', width: '18%', height: '7%' },
  { region: 'foot_right', top: '92%', left: '60%', width: '18%', height: '7%' },
]

const BACK_HOTSPOTS: HotspotData[] = [
  { region: 'back_upper', top: '20%', left: '18%', width: '64%', height: '22%' },
  { region: 'back_lower', top: '42%', left: '22%', width: '56%', height: '18%' },
  { region: 'shoulder_left', top: '18%', left: '5%', width: '20%', height: '12%' },
  { region: 'shoulder_right', top: '18%', left: '75%', width: '20%', height: '12%' },
  { region: 'leg_left', top: '70%', left: '20%', width: '26%', height: '24%' },
  { region: 'leg_right', top: '70%', left: '54%', width: '26%', height: '24%' },
  { region: 'foot_left', top: '92%', left: '20%', width: '20%', height: '7%' },
  { region: 'foot_right', top: '92%', left: '60%', width: '20%', height: '7%' },
]

const FACE_HOTSPOTS: HotspotData[] = [
  { region: 'head_cranium', top: '5%', left: '15%', width: '65%', height: '25%' },
  { region: 'head_face', top: '25%', left: '12%', width: '70%', height: '50%' },
  { region: 'eyes', top: '30%', left: '18%', width: '60%', height: '10%' },
  { region: 'ears', top: '32%', left: '78%', width: '15%', height: '20%' },
  { region: 'mouth_teeth', top: '55%', left: '22%', width: '50%', height: '15%' },
]

// Image: bodyimage_divided.png (1380x752), three figures
// Panel crop: each panel shows one figure via CSS overflow + margin shift
const PANELS = [
  { key: 'front' as const, label: 'Спереду', offsetPct: -12, widthPct: 17, hotspots: FRONT_HOTSPOTS },
  { key: 'back' as const, label: 'Ззаду', offsetPct: -40, widthPct: 15, hotspots: BACK_HOTSPOTS },
  { key: 'face' as const, label: 'Обличчя', offsetPct: -64, widthPct: 34, hotspots: FACE_HOTSPOTS },
]

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
        v-for="panel in PANELS"
        :key="panel.key"
        class="panel"
      >
        <div class="panel-viewport">
          <img
            v-if="!imageErrors[panel.key]"
            :src="bodyImage"
            class="panel-img"
            :style="{
              width: `${100 / (panel.widthPct / 100)}%`,
              marginLeft: `${panel.offsetPct / (panel.widthPct / 100)}%`,
            }"
            alt=""
            @error="imageErrors[panel.key] = true"
          />
          <div v-else class="panel-fallback">
            <i class="pi pi-image" />
          </div>

          <button
            v-for="hs in panel.hotspots"
            :key="hs.region"
            :class="hotspotClasses(hs.region)"
            :style="hotspotStyle(hs)"
            :aria-label="BODY_REGION_LABELS[hs.region] || hs.region"
            @mouseenter="onMouseEnter(hs.region, $event)"
            @mouseleave="onMouseLeave"
            @click="onClick(hs.region)"
            @keydown="onKeydown(hs.region, $event)"
          />
        </div>
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
  gap: 2px;
  align-items: flex-end;
}

.panel {
  flex: 1 1 0;
  min-width: 0;
}

.panel-viewport {
  position: relative;
  overflow: hidden;
  width: 100%;
  aspect-ratio: auto;
}

.panel-img {
  display: block;
  height: auto;
}

.panel-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1 / 2;
  background: #0a0a0a;
  color: #334155;
  font-size: 2rem;
}

.hotspot {
  position: absolute;
  border: 1px solid transparent;
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
    gap: 8px;
  }

  .panel {
    width: 80%;
    max-width: 300px;
  }
}
</style>

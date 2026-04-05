<script setup lang="ts">
import { computed } from 'vue'
import type { CircadianData } from '@/types/weather'

const props = defineProps<{
  data: CircadianData
}>()

const qualityColor = computed(() => {
  const q = props.data.quality
  if (q === 'excellent' || q === 'good') return '#22c55e'
  if (q === 'moderate') return '#eab308'
  if (q === 'poor') return '#ef4444'
  return '#a855f7' // extreme
})

function formatTime(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Kyiv' })
}

function formatHours(hours: number): string {
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  return `${h}г ${m}хв`
}

const dayPercent = computed(() => {
  return Math.min(100, Math.max(0, (props.data.day_length_hours / 24) * 100))
})
</script>

<template>
  <div class="section-card">
    <h3 class="section-title" v-tooltip.top="'Циркадне світло — оцінка природного освітлення, що впливає на біоритми, вироблення мелатоніну та якість сну'">
      Циркадне світло <i class="pi pi-info-circle hint-icon" />
    </h3>

    <div class="circadian-grid">
      <div class="circadian-item" v-tooltip.top="'Час сходу сонця за місцевим часом'">
        <span class="item-label">Схід</span>
        <span class="item-value">{{ formatTime(data.sunrise) }}</span>
      </div>
      <div class="circadian-item" v-tooltip.top="'Час заходу сонця за місцевим часом'">
        <span class="item-label">Захід</span>
        <span class="item-value">{{ formatTime(data.sunset) }}</span>
      </div>
      <div class="circadian-item" v-tooltip.top="'Загальна тривалість світлового дня від сходу до заходу'">
        <span class="item-label">Тривалість дня</span>
        <span class="item-value">{{ formatHours(data.day_length_hours) }}</span>
      </div>
      <div class="circadian-item" v-tooltip.top="'Скільки годин реального яскравого світла з урахуванням хмарності. Хмари зменшують ефективне освітлення на 10–65%'">
        <span class="item-label">Ефективне світло</span>
        <span class="item-value">{{ formatHours(data.effective_light_hours) }}</span>
      </div>
      <div class="circadian-item" v-tooltip.top="'Відсоток неба, закритого хмарами. Впливає на ефективне світло та настрій'">
        <span class="item-label">Хмарність</span>
        <span class="item-value">{{ data.cloud_cover_percent }}%</span>
      </div>
      <div class="circadian-item" v-tooltip.top="'Загальна оцінка природного освітлення:\nВідмінно — ідеально для біоритмів\nДобре — достатньо природного світла\nПомірно — можливий вплив на настрій\nПогано — недостатньо, може впливати на сон'">
        <span class="item-label">Якість</span>
        <span class="quality-badge" :style="{ color: qualityColor, background: qualityColor + '15' }">
          {{ data.quality_label }}
        </span>
      </div>
    </div>

    <div class="day-bar-wrap">
      <div class="day-bar-header">
        <span class="day-bar-label" v-tooltip.top="'Візуальне співвідношення денного та нічного часу за поточну добу'">День / Ніч</span>
        <span class="day-bar-percent">{{ Math.round(dayPercent) }}% день · {{ Math.round(100 - dayPercent) }}% ніч</span>
      </div>
      <div class="day-bar">
        <div class="day-bar-fill" :style="{ width: dayPercent + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 1.25rem;
}
.section-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #a1a1aa;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1rem;
  cursor: help;
}
.circadian-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.circadian-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  cursor: help;
}
.item-label {
  font-size: 0.7rem;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.item-value {
  font-size: 1.125rem;
  font-weight: 300;
  color: #e4e4e7;
}
.quality-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  width: fit-content;
}
.hint-icon {
  font-size: 0.7rem;
  color: #3f3f46;
  vertical-align: middle;
}
.day-bar-wrap {
  margin-top: 0.5rem;
}
.day-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.day-bar-label {
  font-size: 0.7rem;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: help;
}
.day-bar-percent {
  font-size: 0.7rem;
  color: #71717a;
  font-variant-numeric: tabular-nums;
}
.day-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}
.day-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #eab308, #f97316);
  border-radius: 4px;
  transition: width 0.3s;
}
</style>

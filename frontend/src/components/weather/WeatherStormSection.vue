<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { MagneticStormData } from '@/types/weather'
import { getStormColor, formatWeatherDateTime, createWeatherChartOptions } from '@/utils/weatherUtils'

const props = defineProps<{
  data: MagneticStormData
}>()

const severityColor = computed(() => getStormColor(props.data.kp_index))

const chartData = computed(() => {
  const forecast = props.data.forecast
  return {
    labels: forecast.map(e => formatWeatherDateTime(e.period_start)),
    datasets: [{
      label: 'Kp індекс',
      data: forecast.map(e => e.predicted_kp),
      borderColor: '#f97316',
      backgroundColor: 'rgba(249, 115, 22, 0.1)',
      pointRadius: 3,
      pointHoverRadius: 5,
      pointBackgroundColor: forecast.map(e =>
        e.predicted_kp >= 5 ? '#ef4444' : '#22c55e'
      ),
      tension: 0.3,
      fill: true,
    }],
  }
})

const nowLabel = computed(() => {
  const now = Date.now()
  const forecast = props.data.forecast
  if (!forecast.length) return null
  let closest = 0
  let minDiff = Math.abs(new Date(forecast[0].period_start).getTime() - now)
  for (let i = 1; i < forecast.length; i++) {
    const diff = Math.abs(new Date(forecast[i].period_start).getTime() - now)
    if (diff < minDiff) {
      minDiff = diff
      closest = i
    }
  }
  return formatWeatherDateTime(forecast[closest].period_start)
})

const chartOptions = computed(() => createWeatherChartOptions({
  yMin: 0, yMax: 9, yStepSize: 1, maxXTicks: 8,
  annotations: {
    stormThreshold: {
      type: 'line',
      yMin: 5, yMax: 5,
      borderColor: 'rgba(239, 68, 68, 0.4)',
      borderWidth: 1,
      borderDash: [6, 4],
      label: {
        display: true,
        content: 'Шторм (Kp≥5)',
        position: 'start',
        color: '#ef4444',
        font: { size: 10 },
        backgroundColor: 'transparent',
      },
    },
    ...(nowLabel.value ? {
      nowLine: {
        type: 'line',
        xMin: nowLabel.value,
        xMax: nowLabel.value,
        borderColor: 'rgba(161, 161, 170, 0.5)',
        borderWidth: 1,
        borderDash: [4, 4],
        label: {
          display: true,
          content: 'Зараз',
          position: 'start',
          color: '#a1a1aa',
          font: { size: 10 },
          backgroundColor: 'transparent',
        },
      },
    } : {}),
  },
}))
</script>

<template>
  <div class="section-card">
    <h3 class="section-title" v-tooltip.top="'Геомагнітна активність — збурення магнітного поля Землі, спричинені сонячним вітром. Може впливати на самопочуття, особливо серцево-судинну та нервову системи'">
      Магнітні бурі <i class="pi pi-info-circle hint-icon" />
    </h3>

    <div v-if="data.is_storm" class="storm-alert">
      <i class="pi pi-exclamation-triangle" />
      Зараз спостерігається магнітна буря
    </div>

    <div class="storm-current">
      <div class="kp-display" v-tooltip.top="'Kp індекс (0–9) — планетарний показник геомагнітних збурень. 0–3: спокійно, 4: неспокійно, 5+: магнітна буря'">
        <span class="kp-value" :style="{ color: severityColor }">{{ data.kp_index }}</span>
        <span class="kp-label">Kp індекс</span>
      </div>
      <div class="storm-badges">
        <span class="storm-badge" :style="{ color: severityColor, background: severityColor + '15' }" v-tooltip.top="'G-шкала NOAA: G0 — немає бурі, G1 — слабка, G2 — помірна, G3 — сильна, G4 — дуже сильна, G5 — екстремальна'">
          {{ data.g_scale }}
        </span>
        <span class="storm-badge" :style="{ color: severityColor, background: severityColor + '15' }" v-tooltip.top="'Текстова оцінка інтенсивності поточної геомагнітної активності'">
          {{ data.severity }}
        </span>
      </div>
    </div>

    <div v-if="data.health_impact_level" class="health-impact">
      <div class="impact-header">
        <span class="impact-label">Вплив на здоров'я:</span>
        <span class="impact-level" :style="{ color: severityColor }">{{ data.health_impact_level }}</span>
      </div>
      <div v-if="data.affected_systems.length" class="impact-systems">
        <span v-for="system in data.affected_systems" :key="system" class="system-tag">{{ system }}</span>
      </div>
      <ul v-if="data.recommendations.length" class="impact-recommendations">
        <li v-for="rec in data.recommendations" :key="rec">{{ rec }}</li>
      </ul>
    </div>

    <div v-if="data.forecast.length" class="chart-wrap">
      <Chart type="line" :data="chartData" :options="chartOptions" />
    </div>

    <p v-if="data.disclaimer" class="disclaimer">{{ data.disclaimer }}</p>
  </div>
</template>

<style scoped>
.section-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; padding: 1.25rem; }
.section-title { font-size: 0.875rem; font-weight: 500; color: #a1a1aa; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; cursor: help; }
.hint-icon { font-size: 0.7rem; color: #3f3f46; vertical-align: middle; }
.storm-alert { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 4px; padding: 0.75rem 1rem; color: #ef4444; font-size: 0.875rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
.storm-current { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1rem; }
.kp-display { display: flex; flex-direction: column; align-items: center; cursor: help; }
.kp-value { font-size: 2.5rem; font-weight: 300; line-height: 1; }
.kp-label { font-size: 0.625rem; color: #52525b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.25rem; }
.storm-badges { display: flex; flex-direction: column; gap: 0.5rem; }
.storm-badge { font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 2px; text-transform: uppercase; letter-spacing: 0.05em; cursor: help; }
.health-impact { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 4px; padding: 1rem; margin-bottom: 1rem; }
.impact-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
.impact-label { font-size: 0.75rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em; }
.impact-level { font-size: 0.875rem; font-weight: 600; text-transform: uppercase; }
.impact-systems { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem; }
.system-tag { font-size: 0.7rem; padding: 0.2rem 0.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 2px; color: #a1a1aa; }
.impact-recommendations { list-style: none; padding: 0; margin: 0; }
.impact-recommendations li { font-size: 0.8rem; color: #a1a1aa; padding: 0.25rem 0 0.25rem 1rem; position: relative; }
.impact-recommendations li::before { content: '•'; position: absolute; left: 0; color: #52525b; }
.chart-wrap { margin-top: 0.5rem; }
.disclaimer { font-size: 0.625rem; color: #3f3f46; font-style: italic; margin-top: 1rem; line-height: 1.4; }
</style>

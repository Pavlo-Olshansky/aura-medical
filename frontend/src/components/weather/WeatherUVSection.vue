<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { UVData } from '@/types/weather'
import { getUvRiskColor, formatWeatherHour, createWeatherChartOptions } from '@/utils/weatherUtils'

const props = defineProps<{
  data: UVData
}>()

const riskColor = computed(() => getUvRiskColor(props.data.risk_level))

const chartData = computed(() => {
  const forecast = props.data.forecast.slice(0, 24)
  return {
    labels: forecast.map(p => formatWeatherHour(p.forecast_at)),
    datasets: [{
      label: 'UV індекс',
      data: forecast.map(p => p.value),
      borderColor: '#eab308',
      backgroundColor: 'rgba(234, 179, 8, 0.1)',
      pointRadius: 2,
      pointHoverRadius: 5,
      tension: 0.3,
      fill: true,
    }],
  }
})

const chartOptions = createWeatherChartOptions({ yMin: 0, maxXTicks: 8 })
</script>

<template>
  <div class="section-card">
    <h3 class="section-title" v-tooltip.top="'Ультрафіолетовий індекс — інтенсивність сонячного UV-випромінювання. Чим вищий, тим швидше можна отримати опік шкіри'">
      UV індекс <i class="pi pi-info-circle hint-icon" />
    </h3>
    <div class="uv-current">
      <span class="uv-value" :style="{ color: riskColor }" v-tooltip.top="'Поточне значення UV-індексу (0–11+). 0–2: низький, 3–5: помірний, 6–7: високий, 8–10: дуже високий, 11+: екстремальний'">{{ data.value }}</span>
      <span class="uv-risk" :style="{ color: riskColor, background: riskColor + '15' }" v-tooltip.top="'Рівень ризику для шкіри та очей при поточному UV-випромінюванні'">
        {{ data.risk_label }}
      </span>
    </div>
    <div v-if="data.forecast.length" class="chart-wrap">
      <Chart type="line" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.section-card { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); border-radius: 4px; padding: 1.25rem; }
.section-title { font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; cursor: help; }
.hint-icon { font-size: 0.7rem; color: #3f3f46; vertical-align: middle; }
.uv-current { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.uv-value { font-size: 2.5rem; font-weight: 300; line-height: 1; cursor: help; }
.uv-risk { font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.75rem; border-radius: 2px; text-transform: uppercase; letter-spacing: 0.05em; cursor: help; }
.chart-wrap { margin-top: 0.5rem; }
</style>

<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { UVData } from '@/types/weather'

const props = defineProps<{
  data: UVData
}>()

const riskColor = computed(() => {
  const level = props.data.risk_level
  if (level === 'low') return '#22c55e'
  if (level === 'moderate') return '#eab308'
  if (level === 'high') return '#f97316'
  if (level === 'very_high') return '#ef4444'
  return '#a855f7' // extreme
})

const chartData = computed(() => {
  const forecast = props.data.forecast.slice(0, 24)
  return {
    labels: forecast.map(p => {
      const d = new Date(p.forecast_at)
      return `${d.getHours().toString().padStart(2, '0')}:00`
    }),
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

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2.5,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#18181b',
      titleColor: '#e4e4e7',
      bodyColor: '#d4d4d8',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      ticks: { color: '#71717a', maxTicksLimit: 8 },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    y: {
      min: 0,
      ticks: { color: '#71717a' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}
</script>

<template>
  <div class="section-card">
    <h3 class="section-title" title="Ультрафіолетовий індекс — інтенсивність сонячного UV-випромінювання. Чим вищий, тим швидше можна отримати опік шкіри">UV індекс <i class="pi pi-info-circle hint-icon" /></h3>
    <div class="uv-current">
      <span class="uv-value" :style="{ color: riskColor }" title="Поточне значення UV-індексу (0–11+). 0–2: низький, 3–5: помірний, 6–7: високий, 8–10: дуже високий, 11+: екстремальний">{{ data.value }}</span>
      <span class="uv-risk" :style="{ color: riskColor, background: riskColor + '15' }" title="Рівень ризику для шкіри та очей при поточному UV-випромінюванні">
        {{ data.risk_label }}
      </span>
    </div>
    <div v-if="data.forecast.length" class="chart-wrap">
      <Chart type="line" :data="chartData" :options="chartOptions" />
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
}
.uv-current {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.uv-value {
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1;
}
.uv-risk {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.hint-icon {
  font-size: 0.7rem;
  color: #3f3f46;
  vertical-align: middle;
  cursor: help;
}
.chart-wrap {
  margin-top: 0.5rem;
}
</style>

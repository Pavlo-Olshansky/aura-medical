<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { ForecastPoint } from '@/types/weather'

const props = defineProps<{
  forecast: ForecastPoint[]
}>()

function formatHour(iso: string): string {
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:00`
}

function formatDay(iso: string): string {
  const d = new Date(iso)
  const day = d.getDate().toString().padStart(2, '0')
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  return `${day}.${month}`
}

// Today's entries (next 24h)
const todayEntries = computed(() => {
  const now = new Date()
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(23, 59, 59, 999)
  return props.forecast.filter(e => {
    const d = new Date(e.forecast_at)
    return d <= tomorrow
  })
})

const todayChartData = computed(() => ({
  labels: todayEntries.value.map(e => formatHour(e.forecast_at)),
  datasets: [
    {
      label: 'Температура',
      data: todayEntries.value.map(e => e.temperature),
      borderColor: '#f97316',
      backgroundColor: 'rgba(249, 115, 22, 0.1)',
      pointRadius: 3,
      pointHoverRadius: 6,
      tension: 0.3,
      fill: true,
      yAxisID: 'y',
    },
    {
      label: 'Відчувається як',
      data: todayEntries.value.map(e => e.feels_like),
      borderColor: '#8b5cf6',
      backgroundColor: 'transparent',
      borderDash: [4, 4],
      pointRadius: 3,
      pointHoverRadius: 6,
      tension: 0.3,
      fill: false,
      yAxisID: 'y',
    },
  ],
}))

// 5-day: group by day, take min/max temp per day
const dailyData = computed(() => {
  const days = new Map<string, { temps: number[], feels: number[], icons: string[] }>()
  for (const e of props.forecast) {
    const key = formatDay(e.forecast_at)
    if (!days.has(key)) days.set(key, { temps: [], feels: [], icons: [] })
    const d = days.get(key)!
    d.temps.push(e.temperature)
    d.feels.push(e.feels_like)
    d.icons.push(e.condition_icon)
  }
  return Array.from(days.entries()).map(([label, d]) => ({
    label,
    min: Math.min(...d.temps),
    max: Math.max(...d.temps),
    avgFeels: Math.round(d.feels.reduce((a, b) => a + b, 0) / d.feels.length * 10) / 10,
  }))
})

const fiveDayChartData = computed(() => ({
  labels: dailyData.value.map(d => d.label),
  datasets: [
    {
      label: 'Макс',
      data: dailyData.value.map(d => d.max),
      borderColor: '#f97316',
      backgroundColor: 'rgba(249, 115, 22, 0.06)',
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0.3,
      fill: false,
    },
    {
      label: 'Мін',
      data: dailyData.value.map(d => d.min),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.08)',
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0.3,
      fill: '-1',
    },
  ],
}))

const hourlyOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2.5,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: { labels: { color: '#a1a1aa', boxWidth: 12, font: { size: 11 } } },
    tooltip: {
      backgroundColor: '#18181b',
      titleColor: '#e4e4e7',
      bodyColor: '#d4d4d8',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      callbacks: {
        label: (ctx: { dataset: { label: string }, parsed: { y: number } }) =>
          `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}°C`,
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#71717a' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    y: {
      ticks: { color: '#71717a', callback: (v: number) => `${v}°` },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}

const dailyOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2.5,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: { labels: { color: '#a1a1aa', boxWidth: 12, font: { size: 11 } } },
    tooltip: {
      backgroundColor: '#18181b',
      titleColor: '#e4e4e7',
      bodyColor: '#d4d4d8',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      callbacks: {
        label: (ctx: { dataset: { label: string }, parsed: { y: number } }) =>
          `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}°C`,
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#71717a' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    y: {
      ticks: { color: '#71717a', callback: (v: number) => `${v}°` },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}
</script>

<template>
  <div class="forecast-section">
    <div v-if="todayEntries.length" class="section-card">
      <h3 class="section-title" v-tooltip.top="'Погодинний прогноз температури на найближчу добу (кожні 3 години)'">
        Температура сьогодні <i class="pi pi-info-circle hint-icon" />
      </h3>
      <Chart type="line" :data="todayChartData" :options="hourlyOptions" />
    </div>

    <div v-if="dailyData.length > 1" class="section-card">
      <h3 class="section-title" v-tooltip.top="'Мінімальна та максимальна температура на кожен день. Заливка між лініями показує діапазон коливань'">
        Прогноз на 5 днів <i class="pi pi-info-circle hint-icon" />
      </h3>
      <Chart type="line" :data="fiveDayChartData" :options="dailyOptions" />
    </div>
  </div>
</template>

<style scoped>
.forecast-section {
  display: contents;
}
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
.hint-icon {
  font-size: 0.7rem;
  color: #3f3f46;
  vertical-align: middle;
}
</style>

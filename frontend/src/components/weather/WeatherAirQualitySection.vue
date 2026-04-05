<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { AirQualityData } from '@/types/weather'

const props = defineProps<{
  data: AirQualityData
}>()

const aqiColor = computed(() => {
  const aqi = props.data.aqi
  if (aqi === 1) return '#22c55e'
  if (aqi === 2) return '#eab308'
  if (aqi === 3) return '#f97316'
  if (aqi === 4) return '#ef4444'
  return '#a855f7'
})

const pollutants = computed(() => [
  { key: 'PM2.5', value: props.data.pm2_5, unit: 'мкг/м³' },
  { key: 'PM10', value: props.data.pm10, unit: 'мкг/м³' },
  { key: 'O₃', value: props.data.o3, unit: 'мкг/м³' },
  { key: 'NO₂', value: props.data.no2, unit: 'мкг/м³' },
  { key: 'SO₂', value: props.data.so2, unit: 'мкг/м³' },
  { key: 'CO', value: props.data.co, unit: 'мкг/м³' },
  { key: 'NO', value: props.data.no, unit: 'мкг/м³' },
  { key: 'NH₃', value: props.data.nh3, unit: 'мкг/м³' },
])

const chartData = computed(() => {
  const forecast = props.data.forecast.slice(0, 48)
  return {
    labels: forecast.map(p => {
      const d = new Date(p.measured_at)
      return `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth() + 1).toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:00`
    }),
    datasets: [{
      label: 'AQI',
      data: forecast.map(p => p.aqi),
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      pointRadius: 1,
      pointHoverRadius: 4,
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
      min: 1,
      max: 5,
      ticks: { color: '#71717a', stepSize: 1 },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}
</script>

<template>
  <div class="section-card">
    <h3 class="section-title">Якість повітря</h3>

    <div class="aqi-current">
      <span class="aqi-value" :style="{ color: aqiColor }">{{ data.aqi }}</span>
      <span class="aqi-label" :style="{ color: aqiColor, background: aqiColor + '15' }">
        {{ data.label }}
      </span>
    </div>

    <div class="pollutant-grid">
      <div v-for="p in pollutants" :key="p.key" class="pollutant-item">
        <span class="pollutant-name">{{ p.key }}</span>
        <span class="pollutant-value">{{ p.value.toFixed(1) }}</span>
        <span class="pollutant-unit">{{ p.unit }}</span>
      </div>
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
.aqi-current {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.aqi-value {
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1;
}
.aqi-label {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pollutant-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}
.pollutant-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.pollutant-name {
  font-size: 0.625rem;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pollutant-value {
  font-size: 1rem;
  font-weight: 300;
  color: #e4e4e7;
}
.pollutant-unit {
  font-size: 0.575rem;
  color: #3f3f46;
}
.chart-wrap {
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .pollutant-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { MagneticStormData } from '@/types/weather'

const props = defineProps<{
  data: MagneticStormData
}>()

const severityColor = computed(() => {
  const kp = props.data.kp_index
  if (kp < 4) return '#22c55e'
  if (kp < 6) return '#eab308'
  if (kp < 8) return '#f97316'
  return '#ef4444'
})

const chartData = computed(() => {
  const forecast = props.data.forecast
  return {
    labels: forecast.map(e => {
      const d = new Date(e.period_start)
      return `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth() + 1).toString().padStart(2, '0')} ${d.getHours().toString().padStart(2, '0')}:00`
    }),
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
    annotation: {
      annotations: {
        stormThreshold: {
          type: 'line',
          yMin: 5,
          yMax: 5,
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
      },
    },
  },
  scales: {
    x: {
      ticks: { color: '#71717a', maxTicksLimit: 8 },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
    y: {
      min: 0,
      max: 9,
      ticks: { color: '#71717a', stepSize: 1 },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
    },
  },
}
</script>

<template>
  <div class="section-card">
    <h3 class="section-title">Магнітні бурі</h3>

    <div v-if="data.is_storm" class="storm-alert">
      <i class="pi pi-exclamation-triangle" />
      Зараз спостерігається магнітна буря
    </div>

    <div class="storm-current">
      <div class="kp-display">
        <span class="kp-value" :style="{ color: severityColor }">{{ data.kp_index }}</span>
        <span class="kp-label">Kp індекс</span>
      </div>
      <div class="storm-badges">
        <span class="storm-badge" :style="{ color: severityColor, background: severityColor + '15' }">
          {{ data.g_scale }}
        </span>
        <span class="storm-badge" :style="{ color: severityColor, background: severityColor + '15' }">
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
        <span v-for="system in data.affected_systems" :key="system" class="system-tag">
          {{ system }}
        </span>
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
.storm-alert {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 4px;
  padding: 0.75rem 1rem;
  color: #ef4444;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.storm-current {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.kp-display {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.kp-value {
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1;
}
.kp-label {
  font-size: 0.625rem;
  color: #52525b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.25rem;
}
.storm-badges {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.storm-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.health-impact {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.impact-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.impact-label {
  font-size: 0.75rem;
  color: #71717a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.impact-level {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
}
.impact-systems {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.system-tag {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  color: #a1a1aa;
}
.impact-recommendations {
  list-style: none;
  padding: 0;
  margin: 0;
}
.impact-recommendations li {
  font-size: 0.8rem;
  color: #a1a1aa;
  padding: 0.25rem 0;
  padding-left: 1rem;
  position: relative;
}
.impact-recommendations li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #52525b;
}
.chart-wrap {
  margin-top: 0.5rem;
}
.disclaimer {
  font-size: 0.625rem;
  color: #3f3f46;
  font-style: italic;
  margin-top: 1rem;
  line-height: 1.4;
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import { formatDate } from '@/utils/dateUtils'

interface DataPoint {
  date: string
  value: number
  ref_min: number | null
  ref_max: number | null
}

const props = defineProps<{
  biomarkerName: string
  dataPoints: DataPoint[]
}>()

const chartData = computed(() => {
  const sorted = [...props.dataPoints].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  )

  return {
    labels: sorted.map((p) => formatDate(p.date)),
    datasets: [
      {
        label: props.biomarkerName,
        data: sorted.map((p) => p.value),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        pointBackgroundColor: sorted.map((p) => {
          if (p.ref_min != null && p.value < p.ref_min) return '#ef4444'
          if (p.ref_max != null && p.value > p.ref_max) return '#ef4444'
          return '#22c55e'
        }),
        pointBorderColor: sorted.map((p) => {
          if (p.ref_min != null && p.value < p.ref_min) return '#ef4444'
          if (p.ref_max != null && p.value > p.ref_max) return '#ef4444'
          return '#22c55e'
        }),
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.3,
        fill: false,
      },
    ],
  }
})

const chartOptions = computed(() => {
  const sorted = [...props.dataPoints].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  )

  // Get reference range from data (use first available)
  const refMin = sorted.find((p) => p.ref_min != null)?.ref_min ?? null
  const refMax = sorted.find((p) => p.ref_max != null)?.ref_max ?? null

  const annotations: Record<string, any> = {}
  if (refMin != null && refMax != null) {
    annotations.refRange = {
      type: 'box',
      yMin: refMin,
      yMax: refMax,
      backgroundColor: 'rgba(34, 197, 94, 0.08)',
      borderColor: 'rgba(34, 197, 94, 0.2)',
      borderWidth: 1,
    }
  }

  return {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2.5,
    plugins: {
      legend: {
        labels: {
          color: '#a1a1aa',
        },
      },
      tooltip: {
        backgroundColor: '#18181b',
        titleColor: '#e4e4e7',
        bodyColor: '#d4d4d8',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
      },
      annotation: {
        annotations,
      },
    },
    scales: {
      x: {
        ticks: { color: '#71717a' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      y: {
        ticks: { color: '#71717a' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
      },
    },
  }
})
</script>

<template>
  <div class="biomarker-chart">
    <div class="chart-scroll-wrapper">
      <Chart type="line" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.biomarker-chart {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid var(--border-subtle);
}
</style>

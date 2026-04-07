<script setup lang="ts">
import { computed } from 'vue'
import '@/utils/chartSetup'
import Chart from 'primevue/chart'
import type { MetricType } from '@/types'
import { formatDate } from '@/utils/dateUtils'

interface DataPoint {
  date: string
  value: number
  secondary_value: number | null
}

const props = defineProps<{
  metricType: MetricType
  dataPoints: DataPoint[]
}>()

const chartData = computed(() => {
  const sorted = [...props.dataPoints].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
  )

  const datasets: Record<string, unknown>[] = []

  if (props.metricType.has_secondary_value) {
    // Blood pressure: two lines
    datasets.push({
      label: 'Систолічний',
      data: sorted.map((p) => p.value),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      pointBackgroundColor: sorted.map((p) => {
        if (props.metricType.ref_min != null && p.value < props.metricType.ref_min) return '#ef4444'
        if (props.metricType.ref_max != null && p.value > props.metricType.ref_max) return '#ef4444'
        return '#22c55e'
      }),
      pointBorderColor: sorted.map((p) => {
        if (props.metricType.ref_min != null && p.value < props.metricType.ref_min) return '#ef4444'
        if (props.metricType.ref_max != null && p.value > props.metricType.ref_max) return '#ef4444'
        return '#22c55e'
      }),
      pointRadius: 5,
      pointHoverRadius: 7,
      tension: 0.3,
      fill: false,
    })
    datasets.push({
      label: 'Діастолічний',
      data: sorted.map((p) => p.secondary_value),
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      pointBackgroundColor: sorted.map((p) => {
        if (p.secondary_value == null) return '#8b5cf6'
        if (props.metricType.ref_min_secondary != null && p.secondary_value < props.metricType.ref_min_secondary) return '#ef4444'
        if (props.metricType.ref_max_secondary != null && p.secondary_value > props.metricType.ref_max_secondary) return '#ef4444'
        return '#22c55e'
      }),
      pointBorderColor: sorted.map((p) => {
        if (p.secondary_value == null) return '#8b5cf6'
        if (props.metricType.ref_min_secondary != null && p.secondary_value < props.metricType.ref_min_secondary) return '#ef4444'
        if (props.metricType.ref_max_secondary != null && p.secondary_value > props.metricType.ref_max_secondary) return '#ef4444'
        return '#22c55e'
      }),
      pointRadius: 5,
      pointHoverRadius: 7,
      tension: 0.3,
      fill: false,
    })
  } else {
    // Single line for normal metrics
    datasets.push({
      label: props.metricType.name,
      data: sorted.map((p) => p.value),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      pointBackgroundColor: sorted.map((p) => {
        if (props.metricType.ref_min != null && p.value < props.metricType.ref_min) return '#ef4444'
        if (props.metricType.ref_max != null && p.value > props.metricType.ref_max) return '#ef4444'
        return '#22c55e'
      }),
      pointBorderColor: sorted.map((p) => {
        if (props.metricType.ref_min != null && p.value < props.metricType.ref_min) return '#ef4444'
        if (props.metricType.ref_max != null && p.value > props.metricType.ref_max) return '#ef4444'
        return '#22c55e'
      }),
      pointRadius: 5,
      pointHoverRadius: 7,
      tension: 0.3,
      fill: false,
    })
  }

  return {
    labels: sorted.map((p) => formatDate(p.date)),
    datasets,
  }
})

const chartOptions = computed(() => {
  const annotations: Record<string, Record<string, unknown>> = {}

  // Primary reference range
  if (props.metricType.ref_min != null && props.metricType.ref_max != null) {
    annotations.refRange = {
      type: 'box',
      yMin: props.metricType.ref_min,
      yMax: props.metricType.ref_max,
      backgroundColor: 'rgba(34, 197, 94, 0.08)',
      borderColor: 'rgba(34, 197, 94, 0.2)',
      borderWidth: 1,
    }
  }

  // Secondary reference range (for blood pressure diastolic)
  if (
    props.metricType.has_secondary_value &&
    props.metricType.ref_min_secondary != null &&
    props.metricType.ref_max_secondary != null
  ) {
    annotations.refRangeSecondary = {
      type: 'box',
      yMin: props.metricType.ref_min_secondary,
      yMax: props.metricType.ref_max_secondary,
      backgroundColor: 'rgba(139, 92, 246, 0.06)',
      borderColor: 'rgba(139, 92, 246, 0.15)',
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
  <div class="metric-chart">
    <div class="chart-scroll-wrapper">
      <Chart type="line" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.metric-chart {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid var(--border-subtle);
}
</style>

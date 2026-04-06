export function getAqiColor(aqi: number): string {
  if (aqi === 1) return '#22c55e'
  if (aqi === 2) return '#eab308'
  if (aqi === 3) return '#f97316'
  if (aqi === 4) return '#ef4444'
  return '#a855f7'
}

export function getUvRiskColor(level: string): string {
  if (level === 'low') return '#22c55e'
  if (level === 'moderate') return '#eab308'
  if (level === 'high') return '#f97316'
  if (level === 'very_high') return '#ef4444'
  return '#a855f7'
}

export function getStormColor(kp: number): string {
  if (kp < 4) return '#22c55e'
  if (kp < 6) return '#eab308'
  if (kp < 8) return '#f97316'
  return '#ef4444'
}

export function getCircadianColor(quality: string): string {
  if (quality === 'excellent' || quality === 'good') return '#22c55e'
  if (quality === 'moderate') return '#eab308'
  if (quality === 'poor') return '#ef4444'
  return '#a855f7'
}

const WEEKDAYS: Record<string, string[]> = {
  uk: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
}

const LOCALE = 'uk'

function weekday(d: Date): string {
  const days = WEEKDAYS[LOCALE] ?? WEEKDAYS['uk']!
  return days![d.getDay()] ?? ''
}

export function formatWeatherHour(iso: string): string {
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:00`
}

export function formatWeatherDay(iso: string): string {
  const d = new Date(iso)
  const dd = d.getDate().toString().padStart(2, '0')
  const mm = (d.getMonth() + 1).toString().padStart(2, '0')
  return `${weekday(d)} ${dd}.${mm}`
}

export function formatWeatherDateTime(iso: string): string {
  const d = new Date(iso)
  const dd = d.getDate().toString().padStart(2, '0')
  const mm = (d.getMonth() + 1).toString().padStart(2, '0')
  const hh = d.getHours().toString().padStart(2, '0')
  return `${weekday(d)} ${dd}.${mm} ${hh}:00`
}

const CHART_TOOLTIP = {
  backgroundColor: '#18181b',
  titleColor: '#e4e4e7',
  bodyColor: '#d4d4d8',
  borderColor: 'rgba(255, 255, 255, 0.1)',
  borderWidth: 1,
  usePointStyle: true,
  boxHeight: 2,
}

const CHART_GRID = { color: 'rgba(255, 255, 255, 0.05)' }
const CHART_TICKS = { color: '#71717a' }

export function createWeatherChartOptions(opts?: {
  showLegend?: boolean
  yMin?: number
  yMax?: number
  yStepSize?: number
  maxXTicks?: number
  yFormat?: (v: number) => string
  annotations?: Record<string, unknown>
}) {
  return {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2.5,
    interaction: { mode: 'index' as const, intersect: false },
    plugins: {
      legend: opts?.showLegend
        ? { labels: { color: '#a1a1aa', boxWidth: 12, boxHeight: 2, usePointStyle: true, pointStyle: 'line', font: { size: 11 } } }
        : { display: false },
      tooltip: { ...CHART_TOOLTIP },
      ...(opts?.annotations ? { annotation: { annotations: opts.annotations } } : {}),
    },
    scales: {
      x: {
        ticks: { ...CHART_TICKS, ...(opts?.maxXTicks ? { maxTicksLimit: opts.maxXTicks } : {}) },
        grid: CHART_GRID,
      },
      y: {
        ...(opts?.yMin !== undefined ? { min: opts.yMin } : {}),
        ...(opts?.yMax !== undefined ? { max: opts.yMax } : {}),
        ticks: {
          ...CHART_TICKS,
          ...(opts?.yStepSize ? { stepSize: opts.yStepSize } : {}),
          ...(opts?.yFormat ? { callback: opts.yFormat } : {}),
        },
        grid: CHART_GRID,
      },
    },
  }
}

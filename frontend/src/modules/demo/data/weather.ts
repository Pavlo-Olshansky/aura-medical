// Demo weather: realistic Kyiv-ish summary + minimal detail so the
// dashboard weather card and /weather page render meaningfully without
// any real API calls.

import type { WeatherSummary, WeatherDetail } from '@/types/weather'
import { getOrCreate } from '../cache'

export function getDemoWeatherSummary(): WeatherSummary {
  return getOrCreate<WeatherSummary>('weatherSummary', () => ({
    temperature: 14,
    feels_like: 13,
    humidity: 62,
    pressure: 1013,
    condition_description: 'Хмарно з проясненнями',
    condition_icon: '02d',
    wind_speed: 3.4,
    clouds: 40,
    aqi: 2,
    aqi_label: 'Добра',
    kp_index: 2.0,
    storm_severity: 'quiet',
    city: 'Київ',
  }))
}

export function getDemoWeatherDetail(): WeatherDetail {
  return getOrCreate<WeatherDetail>('weatherDetail', () => {
    const now = Date.now()
    const forecast = Array.from({ length: 8 }, (_, i) => ({
      temperature: 14 + Math.sin(i / 2) * 3,
      feels_like: 13 + Math.sin(i / 2) * 3,
      humidity: 60 + i,
      pressure: 1013,
      wind_speed: 3 + (i % 3),
      clouds: 30 + i * 5,
      condition_description: 'Хмарно з проясненнями',
      condition_icon: '02d',
      forecast_at: new Date(now + i * 3 * 3600_000).toISOString(),
    }))
    const today = new Date()
    const sunrise = new Date(today)
    sunrise.setHours(6, 12, 0, 0)
    const sunset = new Date(today)
    sunset.setHours(19, 47, 0, 0)
    return {
      weather: getDemoWeatherSummary(),
      forecast,
      uv: {
        value: 4.2,
        risk_level: 'moderate',
        risk_label: 'Помірний',
        forecast: Array.from({ length: 6 }, (_, i) => ({
          value: Math.max(0, 4.2 - Math.abs(i - 3)),
          forecast_at: new Date(now + i * 3600_000).toISOString(),
        })),
      },
      circadian: {
        sunrise: sunrise.toISOString(),
        sunset: sunset.toISOString(),
        day_length_hours: 13.6,
        cloud_cover_percent: 40,
        effective_light_hours: 8.2,
        quality: 'good',
        quality_label: 'Добре',
      },
      air_quality: {
        aqi: 2,
        label: 'Добра',
        co: 0.4,
        no: 0,
        no2: 18,
        o3: 60,
        so2: 5,
        pm2_5: 12,
        pm10: 20,
        nh3: 1,
        forecast: Array.from({ length: 6 }, (_, i) => ({
          aqi: 2,
          label: 'Добра',
          measured_at: new Date(now + i * 3600_000).toISOString(),
        })),
      },
      magnetic_storm: {
        kp_index: 2.0,
        g_scale: 'G0',
        severity: 'quiet',
        is_storm: false,
        health_impact_level: 'low',
        affected_systems: [],
        recommendations: [],
        disclaimer: null,
        // 8 three-hour windows centered on "now" so the chart renders the
        // standard ~24h Kp forecast curve (WeatherStormSection only renders
        // the chart when forecast.length > 0).
        forecast: Array.from({ length: 8 }, (_, i) => {
          const windowStart = new Date(now + (i - 3) * 3 * 3600_000)
          const windowEnd = new Date(windowStart.getTime() + 3 * 3600_000)
          // Gentle wave 1.5–4.5 — stays sub-storm (Kp<5) for the calm baseline,
          // bumps a little so the line isn't flat.
          const predicted_kp = Math.round((2.5 + Math.sin(i / 1.5) * 1.5) * 10) / 10
          return {
            predicted_kp,
            g_scale: predicted_kp >= 5 ? 'G1' : 'G0',
            severity: predicted_kp >= 5 ? 'minor' : 'quiet',
            is_storm: predicted_kp >= 5,
            period_start: windowStart.toISOString(),
            period_end: windowEnd.toISOString(),
          }
        }),
      },
      city: 'Київ',
    }
  })
}

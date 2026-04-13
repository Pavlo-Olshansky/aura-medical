import { apiClient } from '@/api/client'
import { isDemoMode } from '@/stores/auth'
import { demo } from '@/stores/demoRegistry'
import type { WeatherSummary, WeatherDetail } from '@/types/weather'

export async function getWeatherSummary(): Promise<WeatherSummary | null> {
  if (isDemoMode.value) return demo().getWeatherSummary()
  const response = await apiClient.get<WeatherSummary | null>('/api/v1/weather/summary')
  return response.data
}

export async function getWeatherDetail(): Promise<WeatherDetail> {
  if (isDemoMode.value) return demo().getWeatherDetail()
  const response = await apiClient.get<WeatherDetail>('/api/v1/weather/detail')
  return response.data
}

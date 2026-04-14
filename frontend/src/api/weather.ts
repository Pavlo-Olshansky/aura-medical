import { apiClient } from '@/api/client'
import type { WeatherSummary, WeatherDetail } from '@/types/weather'

export async function getWeatherSummary(): Promise<WeatherSummary | null> {
  const response = await apiClient.get<WeatherSummary | null>('/api/v1/weather/summary')
  return response.data
}

export async function getWeatherDetail(): Promise<WeatherDetail> {
  const response = await apiClient.get<WeatherDetail>('/api/v1/weather/detail')
  return response.data
}

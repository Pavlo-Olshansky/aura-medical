export interface WeatherSummary {
  temperature: number
  feels_like: number
  humidity: number
  pressure: number
  condition_description: string
  condition_icon: string
  wind_speed: number
  clouds: number
  aqi: number | null
  aqi_label: string | null
  kp_index: number | null
  storm_severity: string | null
  city: string
}

export interface UVForecastPoint {
  value: number
  forecast_at: string
}

export interface UVData {
  value: number
  risk_level: string
  risk_label: string
  forecast: UVForecastPoint[]
}

export interface CircadianData {
  sunrise: string | null
  sunset: string | null
  day_length_hours: number
  cloud_cover_percent: number
  effective_light_hours: number
  quality: string
  quality_label: string
}

export interface AQForecastPoint {
  aqi: number
  label: string
  measured_at: string
}

export interface AirQualityData {
  aqi: number
  label: string
  co: number
  no: number
  no2: number
  o3: number
  so2: number
  pm2_5: number
  pm10: number
  nh3: number
  forecast: AQForecastPoint[]
}

export interface StormForecastPoint {
  predicted_kp: number
  g_scale: string
  severity: string
  is_storm: boolean
  period_start: string
  period_end: string
}

export interface MagneticStormData {
  kp_index: number
  g_scale: string
  severity: string
  is_storm: boolean
  health_impact_level: string | null
  affected_systems: string[]
  recommendations: string[]
  disclaimer: string | null
  forecast: StormForecastPoint[]
}

export interface WeatherDetail {
  weather: WeatherSummary | null
  uv: UVData | null
  circadian: CircadianData | null
  air_quality: AirQualityData | null
  magnetic_storm: MagneticStormData | null
  city: string
}

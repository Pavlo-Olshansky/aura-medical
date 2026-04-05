from typing import Optional

from pydantic import BaseModel


class WeatherSummaryResponse(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    condition_description: str
    condition_icon: str
    wind_speed: float
    clouds: int
    aqi: Optional[int] = None
    aqi_label: Optional[str] = None
    kp_index: Optional[float] = None
    storm_severity: Optional[str] = None
    city: str


class UVForecastPoint(BaseModel):
    value: float
    forecast_at: str


class UVData(BaseModel):
    value: float
    risk_level: str
    risk_label: str
    forecast: list[UVForecastPoint] = []


class CircadianData(BaseModel):
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    day_length_hours: float
    cloud_cover_percent: int
    effective_light_hours: float
    quality: str
    quality_label: str


class AQForecastPoint(BaseModel):
    aqi: int
    label: str
    measured_at: str


class AirQualityData(BaseModel):
    aqi: int
    label: str
    co: float
    no: float
    no2: float
    o3: float
    so2: float
    pm2_5: float
    pm10: float
    nh3: float
    forecast: list[AQForecastPoint] = []


class StormForecastPoint(BaseModel):
    predicted_kp: float
    g_scale: str
    severity: str
    is_storm: bool
    period_start: str
    period_end: str


class MagneticStormData(BaseModel):
    kp_index: float
    g_scale: str
    severity: str
    is_storm: bool
    health_impact_level: Optional[str] = None
    affected_systems: list[str] = []
    recommendations: list[str] = []
    disclaimer: Optional[str] = None
    forecast: list[StormForecastPoint] = []


class WeatherDetailResponse(BaseModel):
    weather: Optional[WeatherSummaryResponse] = None
    uv: Optional[UVData] = None
    circadian: Optional[CircadianData] = None
    air_quality: Optional[AirQualityData] = None
    magnetic_storm: Optional[MagneticStormData] = None
    city: str

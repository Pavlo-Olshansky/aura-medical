from __future__ import annotations

import asyncio
import logging

from skypulse import AsyncSkyPulseClient, SkyPulseError

logger = logging.getLogger(__name__)


class WeatherAppService:
    def __init__(self, client: AsyncSkyPulseClient, city: str):
        self._client = client
        self._city = city

    async def get_summary(self) -> dict | None:
        try:
            weather, aq, storm = await asyncio.gather(
                self._client.get_current_weather(city=self._city),
                self._safe(self._client.get_air_quality(city=self._city)),
                self._safe(self._client.get_magnetic_storm()),
            )
        except SkyPulseError:
            logger.warning("Weather summary unavailable", exc_info=True)
            return None

        if weather is None:
            return None

        return {
            "temperature": weather.temperature,
            "feels_like": weather.feels_like,
            "humidity": weather.humidity,
            "pressure": weather.pressure,
            "condition_description": weather.condition.description,
            "condition_icon": weather.condition.icon,
            "wind_speed": weather.wind.speed,
            "clouds": weather.clouds,
            "aqi": aq.aqi if aq else None,
            "aqi_label": aq.label if aq else None,
            "kp_index": storm.kp_index if storm else None,
            "storm_severity": storm.severity if storm else None,
            "city": self._city,
        }

    async def get_detail(self) -> dict:
        weather_result, aq_result, storm_result, uv_result, uv_fc_result, circadian_result, aq_fc_result, storm_fc_result, health_result = await asyncio.gather(
            self._safe(self._client.get_current_weather(city=self._city)),
            self._safe(self._client.get_air_quality(city=self._city)),
            self._safe(self._client.get_magnetic_storm()),
            self._safe(self._client.get_uv_index(city=self._city)),
            self._safe(self._client.get_uv_forecast(city=self._city)),
            self._safe(self._client.get_circadian_light(city=self._city)),
            self._safe(self._client.get_air_quality_forecast(city=self._city)),
            self._safe(self._client.get_magnetic_forecast()),
            self._safe(self._client.get_storm_health_impact()),
        )

        weather_data = None
        if weather_result:
            weather_data = {
                "temperature": weather_result.temperature,
                "feels_like": weather_result.feels_like,
                "humidity": weather_result.humidity,
                "pressure": weather_result.pressure,
                "condition_description": weather_result.condition.description,
                "condition_icon": weather_result.condition.icon,
                "wind_speed": weather_result.wind.speed,
                "wind_direction": weather_result.wind.direction,
                "wind_gust": weather_result.wind.gust,
                "clouds": weather_result.clouds,
                "visibility": weather_result.visibility,
                "city": self._city,
            }

        uv_data = None
        if uv_result:
            uv_data = {
                "value": uv_result.value,
                "risk_level": uv_result.risk_level,
                "risk_label": uv_result.risk_label,
                "forecast": [
                    {"value": e.value, "forecast_at": e.forecast_at.isoformat()}
                    for e in (uv_fc_result or [])
                ],
            }

        circadian_data = None
        if circadian_result:
            circadian_data = {
                "sunrise": circadian_result.sunrise.isoformat() if circadian_result.sunrise else None,
                "sunset": circadian_result.sunset.isoformat() if circadian_result.sunset else None,
                "day_length_hours": circadian_result.day_length_hours,
                "cloud_cover_percent": circadian_result.cloud_cover_percent,
                "effective_light_hours": circadian_result.effective_light_hours,
                "quality": circadian_result.quality,
                "quality_label": circadian_result.quality_label,
            }

        aq_data = None
        if aq_result:
            aq_data = {
                "aqi": aq_result.aqi,
                "label": aq_result.label,
                "co": aq_result.co,
                "no": aq_result.no,
                "no2": aq_result.no2,
                "o3": aq_result.o3,
                "so2": aq_result.so2,
                "pm2_5": aq_result.pm2_5,
                "pm10": aq_result.pm10,
                "nh3": aq_result.nh3,
                "forecast": [
                    {"aqi": e.aqi, "label": e.label, "measured_at": e.measured_at.isoformat()}
                    for e in (aq_fc_result or [])
                ],
            }

        storm_data = None
        if storm_result:
            storm_data = {
                "kp_index": storm_result.kp_index,
                "g_scale": storm_result.g_scale,
                "severity": storm_result.severity,
                "is_storm": storm_result.is_storm,
                "health_impact_level": health_result.level if health_result else None,
                "affected_systems": health_result.affected_systems if health_result else [],
                "recommendations": health_result.recommendations if health_result else [],
                "disclaimer": health_result.disclaimer if health_result else None,
                "forecast": [
                    {
                        "predicted_kp": e.predicted_kp,
                        "g_scale": e.g_scale,
                        "severity": e.severity,
                        "is_storm": e.is_storm,
                        "period_start": e.period_start.isoformat(),
                        "period_end": e.period_end.isoformat(),
                    }
                    for e in (storm_fc_result or [])
                ],
            }

        return {
            "weather": weather_data,
            "uv": uv_data,
            "circadian": circadian_data,
            "air_quality": aq_data,
            "magnetic_storm": storm_data,
            "city": self._city,
        }

    @staticmethod
    async def _safe(coro):
        try:
            return await coro
        except SkyPulseError:
            logger.warning("Weather data fetch failed", exc_info=True)
            return None

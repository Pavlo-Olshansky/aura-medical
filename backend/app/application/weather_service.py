from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from skypulse import AsyncSkyPulseClient

logger = logging.getLogger(__name__)


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _map_weather(w, city: str) -> dict[str, Any]:
    return {
        "temperature": w.temperature,
        "feels_like": w.feels_like,
        "humidity": w.humidity,
        "pressure": w.pressure,
        "condition_description": w.condition.description,
        "condition_icon": w.condition.icon,
        "wind_speed": w.wind.speed,
        "wind_direction": w.wind.direction,
        "wind_gust": w.wind.gust,
        "clouds": w.clouds,
        "visibility": w.visibility,
        "city": city,
    }


def _map_uv(uv, forecast: list | None) -> dict[str, Any]:
    return {
        "value": uv.value,
        "risk_level": uv.risk_level,
        "risk_label": uv.risk_label,
        "forecast": [
            {"value": e.value, "forecast_at": _iso(e.forecast_at)}
            for e in (forecast or [])
        ],
    }


def _map_circadian(c) -> dict[str, Any]:
    return {
        "sunrise": _iso(c.sunrise),
        "sunset": _iso(c.sunset),
        "day_length_hours": c.day_length_hours,
        "cloud_cover_percent": c.cloud_cover_percent,
        "effective_light_hours": c.effective_light_hours,
        "quality": c.quality,
        "quality_label": c.quality_label,
    }


def _map_air_quality(aq, forecast: list | None) -> dict[str, Any]:
    return {
        "aqi": aq.aqi,
        "label": aq.label,
        "co": aq.co,
        "no": aq.no,
        "no2": aq.no2,
        "o3": aq.o3,
        "so2": aq.so2,
        "pm2_5": aq.pm2_5,
        "pm10": aq.pm10,
        "nh3": aq.nh3,
        "forecast": [
            {"aqi": e.aqi, "label": e.label, "measured_at": _iso(e.measured_at)}
            for e in (forecast or [])
        ],
    }


def _map_storm(storm, health, forecast: list | None) -> dict[str, Any]:
    return {
        "kp_index": storm.kp_index,
        "g_scale": storm.g_scale,
        "severity": storm.severity,
        "is_storm": storm.is_storm,
        "health_impact_level": health.level,
        "affected_systems": health.affected_systems,
        "recommendations": health.recommendations,
        "disclaimer": health.disclaimer,
        "forecast": [
            {
                "predicted_kp": e.predicted_kp,
                "g_scale": e.g_scale,
                "severity": e.severity,
                "is_storm": e.is_storm,
                "period_start": _iso(e.period_start),
                "period_end": _iso(e.period_end),
            }
            for e in (forecast or [])
        ],
    }


def _map_forecast(entries) -> list[dict[str, Any]]:
    return [
        {
            "temperature": e.temperature,
            "feels_like": e.feels_like,
            "humidity": e.humidity,
            "pressure": e.pressure,
            "wind_speed": e.wind.speed,
            "clouds": e.clouds,
            "condition_description": e.condition.description,
            "condition_icon": e.condition.icon,
            "forecast_at": _iso(e.forecast_at),
        }
        for e in entries
    ]


_EMPTY_DETAIL: dict[str, Any] = {
    "weather": None, "forecast": [], "uv": None,
    "circadian": None, "air_quality": None, "magnetic_storm": None,
}


class WeatherAppService:
    def __init__(self, client: AsyncSkyPulseClient | None, city: str):
        self._client = client
        self._city = city

    async def _resolve_coords(self) -> tuple[float, float]:
        assert self._client is not None
        locations = await self._client.geocode(self._city, limit=1)
        if not locations:
            raise ValueError(f"City not found: {self._city}")
        return locations[0].latitude, locations[0].longitude

    async def get_summary(self) -> dict | None:
        if not self._client:
            return None
        try:
            lat, lon = await self._resolve_coords()
            weather, aq, storm = await asyncio.gather(
                self._safe(self._client.get_current_weather(lat=lat, lon=lon)),
                self._safe(self._client.get_air_quality(lat=lat, lon=lon)),
                self._safe(self._client.get_magnetic_storm()),
            )
        except Exception:
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
        if not self._client:
            return {**_EMPTY_DETAIL, "city": self._city}

        try:
            lat, lon = await self._resolve_coords()
        except Exception:
            logger.warning("Failed to resolve city coordinates", exc_info=True)
            return {**_EMPTY_DETAIL, "city": self._city}

        (
            weather_result, forecast_result, aq_result, storm_result,
            uv_result, uv_fc_result, circadian_result, aq_fc_result, storm_fc_result,
        ) = await asyncio.gather(
            self._safe(self._client.get_current_weather(lat=lat, lon=lon)),
            self._safe(self._client.get_forecast(lat=lat, lon=lon)),
            self._safe(self._client.get_air_quality(lat=lat, lon=lon)),
            self._safe(self._client.get_magnetic_storm()),
            self._safe(self._client.get_uv_index(lat=lat, lon=lon)),
            self._safe(self._client.get_uv_forecast(lat=lat, lon=lon)),
            self._safe(self._client.get_circadian_light(lat=lat, lon=lon)),
            self._safe(self._client.get_air_quality_forecast(lat=lat, lon=lon)),
            self._safe(self._client.get_magnetic_forecast()),
        )

        storm_data = None
        if storm_result:
            from skypulse._storm_mapping import get_health_impact
            health = get_health_impact(storm_result.kp_index, storm_result.g_scale, "uk")
            storm_data = _map_storm(storm_result, health, storm_fc_result)

        return {
            "weather": _map_weather(weather_result, self._city) if weather_result else None,
            "forecast": _map_forecast(forecast_result.entries) if forecast_result else [],
            "uv": _map_uv(uv_result, uv_fc_result) if uv_result else None,
            "circadian": _map_circadian(circadian_result) if circadian_result else None,
            "air_quality": _map_air_quality(aq_result, aq_fc_result) if aq_result else None,
            "magnetic_storm": storm_data,
            "city": self._city,
        }

    @staticmethod
    async def _safe(coro: Coroutine) -> Any:
        try:
            return await coro
        except Exception:
            logger.warning("Weather data fetch failed", exc_info=True)
            return None

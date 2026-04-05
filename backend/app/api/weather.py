from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_weather_service
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.infrastructure.models.user import UserModel
from app.schemas.weather import WeatherDetailResponse, WeatherSummaryResponse

if TYPE_CHECKING:
    from app.application.weather_service import WeatherAppService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", response_model=WeatherSummaryResponse | None)
async def get_weather_summary(
    service: WeatherAppService = Depends(get_weather_service),
):
    data = await service.get_summary()
    if data is None:
        return JSONResponse(content=None, status_code=200)
    return data


@router.get("/detail", response_model=WeatherDetailResponse)
async def get_weather_detail(
    service: WeatherAppService = Depends(get_weather_service),
):
    return await service.get_detail()


@router.post("/detect-city")
async def detect_city(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    client = request.app.state.skypulse
    if not client:
        return {"city": None, "saved": False}

    try:
        location = await client.get_location()
        city = location.name
    except Exception:
        logger.warning("City detection failed", exc_info=True)
        return {"city": None, "saved": False}

    saved = False
    if current_user.weather_city_auto and not current_user.weather_city and city:
        try:
            await session.execute(
                update(UserModel).where(UserModel.id == current_user.id).values(weather_city=city)
            )
            await session.commit()
            saved = True
        except Exception:
            await session.rollback()
            logger.warning("Failed to save detected city", exc_info=True)

    return {"city": city, "saved": saved}

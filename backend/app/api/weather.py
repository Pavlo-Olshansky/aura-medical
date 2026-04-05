from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user, get_weather_service
from app.application.weather_service import WeatherAppService
from app.domain.entities import User
from app.schemas.weather import WeatherDetailResponse, WeatherSummaryResponse

router = APIRouter()


@router.get("/summary", response_model=WeatherSummaryResponse | None)
async def get_weather_summary(
    current_user: User = Depends(get_current_user),
    service: WeatherAppService = Depends(get_weather_service),
):
    data = await service.get_summary()
    if data is None:
        return JSONResponse(content=None, status_code=200)
    return data


@router.get("/detail", response_model=WeatherDetailResponse)
async def get_weather_detail(
    current_user: User = Depends(get_current_user),
    service: WeatherAppService = Depends(get_weather_service),
):
    return await service.get_detail()

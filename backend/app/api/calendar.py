from datetime import date

from fastapi import APIRouter, Depends

from app.api.dependencies import get_calendar_service, get_current_user
from app.application.calendar_service import CalendarAppService
from app.domain.entities import User
from app.schemas.calendar import CalendarEventsListResponse

router = APIRouter()


@router.get("/events", response_model=CalendarEventsListResponse)
async def get_calendar_events(
    date_from: date,
    date_to: date,
    current_user: User = Depends(get_current_user),
    service: CalendarAppService = Depends(get_calendar_service),
):
    events = await service.get_events(current_user.id, date_from, date_to)
    return CalendarEventsListResponse(
        events=events,
        date_from=date_from,
        date_to=date_to,
    )

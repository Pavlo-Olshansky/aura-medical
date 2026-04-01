import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_timeline_service
from app.application.timeline_service import TimelineAppService, TimelineEvent
from app.domain.entities import User
from app.schemas.timeline import TimelineEventResponse, TimelineListResponse

router = APIRouter()


def _to_response(e: TimelineEvent) -> TimelineEventResponse:
    route_map = {
        "visit": f"/visits/{e.entity_id}",
        "treatment": f"/treatments/{e.entity_id}",
        "lab_result": f"/lab-results/{e.entity_id}",
        "vaccination": f"/vaccinations/{e.entity_id}",
    }
    return TimelineEventResponse(
        event_type=e.event_type, event_id=e.id, date=e.date,
        title=e.title, subtitle=e.subtitle or "",
        route=route_map.get(e.event_type, ""),
    )


@router.get("/", response_model=TimelineListResponse)
async def list_timeline(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: TimelineAppService = Depends(get_timeline_service),
):
    items, total = await service.list(current_user.id, event_type, date_from, date_to, page, size)
    pages = math.ceil(total / size) if total > 0 else 1
    return TimelineListResponse(
        items=[_to_response(e) for e in items],
        total=total, page=page, size=size, pages=pages,
    )

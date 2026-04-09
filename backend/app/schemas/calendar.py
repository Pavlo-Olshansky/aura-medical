from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel


class CalendarEventResponse(BaseModel):
    id: int
    event_type: Literal["visit", "treatment"]
    title: str
    start: datetime
    end: datetime
    all_day: bool
    color: str
    url: str
    extra: dict[str, Any]


class CalendarEventsListResponse(BaseModel):
    events: list[CalendarEventResponse]
    date_from: date
    date_to: date

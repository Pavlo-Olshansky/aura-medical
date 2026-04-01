from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TimelineEventResponse(BaseModel):
    event_type: str
    event_id: int
    date: datetime
    title: str
    subtitle: str
    body_region: Optional[str] = None
    route: str


class TimelineListResponse(BaseModel):
    items: List[TimelineEventResponse]
    total: int
    page: int
    size: int
    pages: int

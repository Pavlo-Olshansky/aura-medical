from datetime import datetime

from pydantic import BaseModel


class ReminderResponse(BaseModel):
    entity_type: str
    entity_id: int
    reminder_type: str
    title: str
    event_date: datetime
    route: str


class RemindersListResponse(BaseModel):
    items: list[ReminderResponse]
    count: int


class DismissRequest(BaseModel):
    entity_type: str
    entity_id: int
    reminder_type: str

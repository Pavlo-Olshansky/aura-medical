from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TreatmentCreate(BaseModel):
    date_start: datetime
    name: str
    days: int
    receipt: str


class TreatmentUpdate(BaseModel):
    date_start: Optional[datetime] = None
    name: Optional[str] = None
    days: Optional[int] = None
    receipt: Optional[str] = None


class TreatmentResponse(BaseModel):
    id: int
    date_start: datetime
    name: str
    days: int
    receipt: str
    status: str
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}


class TreatmentListResponse(BaseModel):
    items: List[TreatmentResponse]
    total: int
    page: int
    size: int
    pages: int

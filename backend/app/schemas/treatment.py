from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TreatmentCreate(BaseModel):
    date_start: datetime
    name: str
    days: int = Field(ge=1)
    receipt: str
    body_region: Optional[str] = None


class TreatmentUpdate(BaseModel):
    date_start: Optional[datetime] = None
    name: Optional[str] = None
    days: Optional[int] = None
    receipt: Optional[str] = None
    body_region: Optional[str] = None


class TreatmentResponse(BaseModel):
    id: int
    date_start: datetime
    name: str
    days: int = Field(ge=1)
    receipt: str
    status: str
    body_region: Optional[str] = None
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}

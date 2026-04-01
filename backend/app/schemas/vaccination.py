from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class VaccinationCreate(BaseModel):
    date: datetime
    vaccine_name: str
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    dose_number: int
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = ""


class VaccinationUpdate(BaseModel):
    date: Optional[datetime] = None
    vaccine_name: Optional[str] = None
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    dose_number: Optional[int] = None
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = ""


class VaccinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    vaccine_name: str
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    dose_number: int
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = ""
    has_document: bool
    status: str
    created: datetime
    updated: datetime


class VaccinationListResponse(BaseModel):
    items: List[VaccinationResponse]
    total: int
    page: int
    size: int
    pages: int

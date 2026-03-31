from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BodyRegionSummary(BaseModel):
    visit_count: int
    active_treatment_count: int
    last_visit_date: Optional[datetime] = None
    visits_last_year: int


class BodyMapSummaryResponse(BaseModel):
    regions: dict[str, BodyRegionSummary]
    unmapped_visit_count: int
    whole_body_visit_count: int


class BodyMapVisitItem(BaseModel):
    id: int
    date: datetime
    doctor: Optional[str] = None
    position_name: Optional[str] = None
    procedure_name: Optional[str] = None
    clinic_name: Optional[str] = None
    has_document: bool


class BodyMapTreatmentItem(BaseModel):
    id: int
    name: str
    date_start: datetime
    days: int
    date_end: datetime
    status: str


class BodyRegionDetailResponse(BaseModel):
    region: str
    label: str
    visits: list[BodyMapVisitItem]
    treatments: list[BodyMapTreatmentItem]

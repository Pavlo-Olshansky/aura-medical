from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SearchGroup(BaseModel, Generic[T]):
    items: list[T]
    total: int


class VisitSearchItem(BaseModel):
    id: int
    date: datetime
    doctor: Optional[str] = None
    position_name: Optional[str] = None
    procedure_name: Optional[str] = None
    clinic_name: Optional[str] = None
    city_name: Optional[str] = None
    body_region: Optional[str] = None
    comment: Optional[str] = None


class TreatmentSearchItem(BaseModel):
    id: int
    date_start: datetime
    name: str
    days: int
    status: str
    body_region: Optional[str] = None


class LabResultSearchItem(BaseModel):
    id: int
    date: datetime
    notes: Optional[str] = None
    biomarker_names: list[str]
    visit_id: Optional[int] = None


class VaccinationSearchItem(BaseModel):
    id: int
    date: datetime
    vaccine_name: str
    dose_number: int
    manufacturer: Optional[str] = None
    notes: Optional[str] = None


class SearchResponse(BaseModel):
    visits: SearchGroup[VisitSearchItem]
    treatments: SearchGroup[TreatmentSearchItem]
    lab_results: SearchGroup[LabResultSearchItem]
    vaccinations: SearchGroup[VaccinationSearchItem]

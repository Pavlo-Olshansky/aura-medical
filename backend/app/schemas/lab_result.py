from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class LabTestEntryCreate(BaseModel):
    biomarker_id: Optional[int] = None
    biomarker_name: str
    value: Decimal
    unit: str
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None


class LabTestEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    biomarker_id: Optional[int] = None
    biomarker_name: str
    value: Decimal
    unit: str
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    is_normal: Optional[bool] = None


class LabResultCreate(BaseModel):
    visit_id: Optional[int] = None
    date: datetime
    notes: Optional[str] = ""
    entries: List[LabTestEntryCreate]


class LabResultUpdate(BaseModel):
    visit_id: Optional[int] = None
    date: Optional[datetime] = None
    notes: Optional[str] = ""
    entries: Optional[List[LabTestEntryCreate]] = None


class LabResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: Optional[int] = None
    date: datetime
    notes: Optional[str] = ""
    entries: List[LabTestEntryResponse]
    created: datetime
    updated: datetime


class LabResultListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: Optional[int] = None
    date: datetime
    notes: Optional[str] = ""
    entries_count: int
    out_of_range_count: int
    visit_date: Optional[str] = None
    visit_procedure: Optional[str] = None
    created: datetime
    updated: datetime


class LabResultListResponse(BaseModel):
    items: List[LabResultListItem]
    total: int
    page: int
    size: int
    pages: int


class BiomarkerTrendPoint(BaseModel):
    date: datetime
    value: Decimal
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None


class BiomarkerTrendResponse(BaseModel):
    biomarker_name: str
    data_points: List[BiomarkerTrendPoint]

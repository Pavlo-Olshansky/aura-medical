from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class VisitCreate(BaseModel):
    date: datetime
    position_id: Optional[int] = None
    doctor: Optional[str] = None
    procedure_id: Optional[int] = None
    procedure_details: Optional[str] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    link: Optional[str] = None
    comment: Optional[str] = None


class VisitUpdate(BaseModel):
    date: Optional[datetime] = None
    position_id: Optional[int] = None
    doctor: Optional[str] = None
    procedure_id: Optional[int] = None
    procedure_details: Optional[str] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    link: Optional[str] = None
    comment: Optional[str] = None


class ReferenceInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    position: Optional[ReferenceInline] = None
    doctor: Optional[str] = None
    procedure: Optional[ReferenceInline] = None
    procedure_details: Optional[str] = None
    clinic: Optional[ReferenceInline] = None
    city: Optional[ReferenceInline] = None
    document: Optional[str] = None
    has_document: bool = False
    link: Optional[str] = None
    comment: Optional[str] = None
    created: datetime
    updated: datetime


class VisitListResponse(BaseModel):
    items: List[VisitResponse]
    total: int
    page: int
    size: int
    pages: int

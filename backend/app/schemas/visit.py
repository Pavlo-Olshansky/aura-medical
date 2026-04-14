from datetime import datetime
from decimal import Decimal
from typing import Optional

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
    body_region: Optional[str] = None
    price: Optional[Decimal] = None


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
    body_region: Optional[str] = None
    price: Optional[Decimal] = None


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
    body_region: Optional[str] = None
    link: Optional[str] = None
    comment: Optional[str] = None
    price: Optional[Decimal] = None
    created: datetime
    updated: datetime

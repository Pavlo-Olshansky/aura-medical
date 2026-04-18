from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


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

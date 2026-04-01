from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BiomarkerReferenceCreate(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    unit: str
    category: str
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_male: Optional[Decimal] = None
    ref_max_male: Optional[Decimal] = None
    ref_min_female: Optional[Decimal] = None
    ref_max_female: Optional[Decimal] = None


class BiomarkerReferenceUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_male: Optional[Decimal] = None
    ref_max_male: Optional[Decimal] = None
    ref_min_female: Optional[Decimal] = None
    ref_max_female: Optional[Decimal] = None


class BiomarkerReferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: Optional[str] = None
    unit: str
    category: str
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_male: Optional[Decimal] = None
    ref_max_male: Optional[Decimal] = None
    ref_min_female: Optional[Decimal] = None
    ref_max_female: Optional[Decimal] = None
    sort_order: int
    created: datetime
    updated: datetime

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MetricTypeCreate(BaseModel):
    name: str
    unit: str
    has_secondary_value: bool = False
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None


class MetricTypeUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    has_secondary_value: Optional[bool] = None
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None


class MetricTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    unit: str
    has_secondary_value: bool
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None
    sort_order: int
    created: datetime
    updated: datetime

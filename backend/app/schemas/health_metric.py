from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.metric_type import MetricTypeResponse


class HealthMetricCreate(BaseModel):
    metric_type_id: int
    date: datetime
    value: Decimal
    secondary_value: Optional[Decimal] = None
    notes: Optional[str] = None


class HealthMetricUpdate(BaseModel):
    metric_type_id: Optional[int] = None
    date: Optional[datetime] = None
    value: Optional[Decimal] = None
    secondary_value: Optional[Decimal] = None
    notes: Optional[str] = None


class HealthMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_type_id: int
    metric_type: MetricTypeResponse
    date: datetime
    value: Decimal
    secondary_value: Optional[Decimal] = None
    notes: Optional[str] = None
    created: datetime
    updated: datetime


class HealthMetricListResponse(BaseModel):
    items: List[HealthMetricResponse]
    total: int
    page: int
    size: int
    pages: int


class MetricTrendPoint(BaseModel):
    date: datetime
    value: Decimal
    secondary_value: Optional[Decimal] = None


class MetricTrendResponse(BaseModel):
    metric_type: str
    unit: str
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None
    data_points: List[MetricTrendPoint]

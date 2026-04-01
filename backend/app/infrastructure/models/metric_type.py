from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class MetricTypeModel(BaseModel):
    __tablename__ = "metric_type"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    has_secondary_value: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ref_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_min_secondary: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max_secondary: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

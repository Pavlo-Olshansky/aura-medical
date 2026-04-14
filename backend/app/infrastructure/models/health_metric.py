from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import SoftDeleteModel


class HealthMetricModel(SoftDeleteModel):
    __tablename__ = "health_metric"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    metric_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("metric_type.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    secondary_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    metric_type = relationship("MetricTypeModel", lazy="selectin")

    __table_args__ = (
        Index("ix_health_metric_user_id", "user_id"),
        Index("ix_health_metric_date", "date"),
        Index("ix_health_metric_metric_type_id", "metric_type_id"),
        Index("ix_health_metric_user_date", "user_id", "date"),
        Index("ix_health_metric_user_deleted_at", "user_id", "deleted_at"),
    )

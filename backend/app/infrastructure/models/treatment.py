from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import SoftDeleteModel


class TreatmentModel(SoftDeleteModel):
    __tablename__ = "treatment"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    date_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    receipt: Mapped[str] = mapped_column(String(1024), nullable=False)
    body_region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    __table_args__ = (
        Index("ix_treatment_user_id", "user_id"),
        Index("ix_treatment_user_date_start", "user_id", "date_start"),
        Index("ix_treatment_user_deleted_at", "user_id", "deleted_at"),
        CheckConstraint("days >= 1", name="ck_treatment_days_positive"),
    )

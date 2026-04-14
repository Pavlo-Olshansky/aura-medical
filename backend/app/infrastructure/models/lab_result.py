from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel, SoftDeleteModel


class LabResultModel(SoftDeleteModel):
    __tablename__ = "lab_result"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    visit_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("visit.id", ondelete="SET NULL"), nullable=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    entries = relationship("LabTestEntryModel", back_populates="lab_result", cascade="all, delete-orphan", lazy="selectin")
    visit = relationship("VisitModel", lazy="selectin")

    __table_args__ = (
        Index("ix_lab_result_user_id", "user_id"),
        Index("ix_lab_result_date", "date"),
        Index("ix_lab_result_visit_id", "visit_id"),
        Index("ix_lab_result_user_date", "user_id", "date"),
        Index("ix_lab_result_user_deleted_at", "user_id", "deleted_at"),
    )


class LabTestEntryModel(BaseModel):
    __tablename__ = "lab_test_entry"

    lab_result_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lab_result.id", ondelete="CASCADE"), nullable=False
    )
    biomarker_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("biomarker_reference.id", ondelete="SET NULL"), nullable=True
    )
    biomarker_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    ref_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)

    lab_result = relationship("LabResultModel", back_populates="entries")

    __table_args__ = (
        Index("ix_lab_test_entry_lab_result_id", "lab_result_id"),
        Index("ix_lab_test_entry_biomarker_id", "biomarker_id"),
    )

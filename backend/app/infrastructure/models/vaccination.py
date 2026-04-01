from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import SoftDeleteModel


class VaccinationModel(SoftDeleteModel):
    __tablename__ = "vaccination"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vaccine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lot_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dose_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    next_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("ix_vaccination_user_id", "user_id"),
        Index("ix_vaccination_date", "date"),
    )

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import SoftDeleteModel


class Visit(SoftDeleteModel):
    __tablename__ = "visit"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    position_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("position.id", ondelete="SET NULL"), nullable=True
    )
    doctor: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    procedure_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("procedure.id", ondelete="SET NULL"), nullable=True
    )
    procedure_details: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    clinic_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("clinic.id", ondelete="SET NULL"), nullable=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("city.id", ondelete="SET NULL"), nullable=True
    )
    document: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    link: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    user = relationship("User", lazy="selectin")
    position = relationship("Position", lazy="selectin")
    procedure = relationship("Procedure", lazy="selectin")
    clinic = relationship("Clinic", lazy="selectin")
    city = relationship("City", lazy="selectin")

    __table_args__ = (
        Index("ix_visit_user_id", "user_id"),
        Index("ix_visit_date", "date"),
        Index("ix_visit_user_date", "user_id", "date"),
    )

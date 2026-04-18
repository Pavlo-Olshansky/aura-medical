from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class BiomarkerReferenceModel(BaseModel):
    __tablename__ = "biomarker_reference"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ref_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_min_male: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max_male: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_min_female: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    ref_max_female: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("name", "unit", name="uq_biomarker_name_unit"),
    )

import datetime
import enum
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, Enum, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class SexEnum(str, enum.Enum):
    male = "male"
    female = "female"


class UserModel(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Profile fields
    sex: Mapped[str] = mapped_column(
        Enum(SexEnum, values_callable=lambda e: [x.value for x in e]),
        nullable=False, server_default="male",
    )
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default="1997-07-29")
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chronic_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

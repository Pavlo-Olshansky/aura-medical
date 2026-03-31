from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class SexEnum(str, Enum):
    male = "male"
    female = "female"


class BloodTypeEnum(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class ProfileResponse(BaseModel):
    sex: str
    date_of_birth: date
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    sex: SexEnum
    date_of_birth: date
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    blood_type: Optional[BloodTypeEnum] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        today = date.today()
        if v > today:
            raise ValueError("Дата народження не може бути в майбутньому")
        min_date = today.replace(year=today.year - 120)
        if v < min_date:
            raise ValueError("Дата народження занадто давня")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 30 or v > 250):
            raise ValueError("Зріст повинен бути від 30 до 250 см")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 1 or v > 500):
            raise ValueError("Вага повинна бути від 1 до 500 кг")
        return v

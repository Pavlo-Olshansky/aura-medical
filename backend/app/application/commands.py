from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class CreateVisitCommand:
    date: datetime
    position_id: Optional[int] = None
    doctor: Optional[str] = None
    procedure_id: Optional[int] = None
    procedure_details: Optional[str] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    link: Optional[str] = None
    comment: Optional[str] = None
    body_region: Optional[str] = None


@dataclass
class UpdateVisitCommand:
    date: Optional[datetime] = None
    position_id: Optional[int] = None
    doctor: Optional[str] = None
    procedure_id: Optional[int] = None
    procedure_details: Optional[str] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    link: Optional[str] = None
    comment: Optional[str] = None
    body_region: Optional[str] = None


@dataclass
class CreateTreatmentCommand:
    date_start: datetime
    name: str
    days: int
    receipt: str
    body_region: Optional[str] = None


@dataclass
class UpdateTreatmentCommand:
    date_start: Optional[datetime] = None
    name: Optional[str] = None
    days: Optional[int] = None
    receipt: Optional[str] = None
    body_region: Optional[str] = None


@dataclass
class VisitFilter:
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    procedure_id: Optional[int] = None
    position_id: Optional[int] = None
    body_region: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

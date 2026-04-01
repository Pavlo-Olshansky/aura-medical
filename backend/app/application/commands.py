from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
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


@dataclass
class CreateBiomarkerReferenceCommand:
    name: str
    unit: str
    category: str
    abbreviation: Optional[str] = None
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_male: Optional[Decimal] = None
    ref_max_male: Optional[Decimal] = None
    ref_min_female: Optional[Decimal] = None
    ref_max_female: Optional[Decimal] = None
    sort_order: int = 0


@dataclass
class UpdateBiomarkerReferenceCommand:
    name: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    abbreviation: Optional[str] = None
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_male: Optional[Decimal] = None
    ref_max_male: Optional[Decimal] = None
    ref_min_female: Optional[Decimal] = None
    ref_max_female: Optional[Decimal] = None
    sort_order: Optional[int] = None


@dataclass
class CreateMetricTypeCommand:
    name: str
    unit: str
    has_secondary_value: bool = False
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None
    sort_order: int = 0


@dataclass
class UpdateMetricTypeCommand:
    name: Optional[str] = None
    unit: Optional[str] = None
    has_secondary_value: Optional[bool] = None
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None
    ref_min_secondary: Optional[Decimal] = None
    ref_max_secondary: Optional[Decimal] = None
    sort_order: Optional[int] = None


@dataclass
class LabTestEntryData:
    biomarker_id: Optional[int] = None
    biomarker_name: str = ""
    value: Decimal = Decimal("0")
    unit: str = ""
    ref_min: Optional[Decimal] = None
    ref_max: Optional[Decimal] = None


@dataclass
class CreateLabResultCommand:
    date: datetime = field(default_factory=datetime.now)
    visit_id: Optional[int] = None
    notes: Optional[str] = None
    entries: list[LabTestEntryData] = field(default_factory=list)


@dataclass
class UpdateLabResultCommand:
    date: Optional[datetime] = None
    visit_id: Optional[int] = None
    notes: Optional[str] = None
    entries: Optional[list[LabTestEntryData]] = None


@dataclass
class CreateHealthMetricCommand:
    metric_type_id: int = 0
    date: datetime = field(default_factory=datetime.now)
    value: Decimal = Decimal("0")
    secondary_value: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass
class UpdateHealthMetricCommand:
    metric_type_id: Optional[int] = None
    date: Optional[datetime] = None
    value: Optional[Decimal] = None
    secondary_value: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass
class CreateVaccinationCommand:
    date: datetime = field(default_factory=datetime.now)
    vaccine_name: str = ""
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    dose_number: int = 1
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class UpdateVaccinationCommand:
    date: Optional[datetime] = None
    vaccine_name: Optional[str] = None
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    dose_number: Optional[int] = None
    next_due_date: Optional[datetime] = None
    notes: Optional[str] = None

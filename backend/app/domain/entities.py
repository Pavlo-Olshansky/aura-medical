from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from app.domain.exceptions import DomainError
from app.domain.value_objects import BodyRegion

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


@dataclass
class SoftDeletable:
    deleted_at: Optional[datetime] = None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(KYIV_TZ)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    is_active: bool
    sex: str = "male"
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    def ensure_active(self) -> None:
        if not self.is_active:
            raise DomainError("User is not active")


@dataclass
class Reference:
    id: Optional[int]
    name: str
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


@dataclass
class Visit(SoftDeletable):
    id: Optional[int] = None
    user_id: int = 0
    date: datetime = field(default_factory=lambda: datetime.now(KYIV_TZ))
    position_id: Optional[int] = None
    doctor: Optional[str] = None
    procedure_id: Optional[int] = None
    procedure_details: Optional[str] = None
    clinic_id: Optional[int] = None
    city_id: Optional[int] = None
    document: Optional[str] = None
    link: Optional[str] = None
    comment: Optional[str] = None
    body_region: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    # Read-model projection fields — populated by repositories for API response building.
    # Never used for write operations or domain logic.
    position: Optional[Reference] = field(default=None, repr=False)
    procedure: Optional[Reference] = field(default=None, repr=False)
    clinic: Optional[Reference] = field(default=None, repr=False)
    city: Optional[Reference] = field(default=None, repr=False)

    @property
    def has_document(self) -> bool:
        return bool(self.document)

    def attach_document(self, path: str) -> None:
        self.document = path

    def set_body_region(self, region: Optional[str]) -> None:
        if region is not None:
            BodyRegion.validate(region)
        self.body_region = region


@dataclass
class Treatment(SoftDeletable):
    id: Optional[int] = None
    user_id: int = 0
    date_start: datetime = field(default_factory=lambda: datetime.now(KYIV_TZ))
    name: str = ""
    days: int = 0
    receipt: str = ""
    body_region: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @property
    def status(self) -> str:
        now = datetime.now(KYIV_TZ)
        end_date = self.date_start + timedelta(days=self.days)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=KYIV_TZ)
        return "active" if end_date > now else "completed"

    @property
    def end_date(self) -> datetime:
        return self.date_start + timedelta(days=self.days)

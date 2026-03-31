from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class PositionModel(BaseModel):
    __tablename__ = "position"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class ProcedureModel(BaseModel):
    __tablename__ = "procedure"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class ClinicModel(BaseModel):
    __tablename__ = "clinic"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class CityModel(BaseModel):
    __tablename__ = "city"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Position(BaseModel):
    __tablename__ = "position"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class Procedure(BaseModel):
    __tablename__ = "procedure"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class Clinic(BaseModel):
    __tablename__ = "clinic"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)


class City(BaseModel):
    __tablename__ = "city"
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

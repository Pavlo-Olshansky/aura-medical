# Backward-compat shim — re-exports with original names for existing code
from app.infrastructure.models.base import Base, BaseModel, SoftDeleteModel
from app.infrastructure.models.reference import (
    CityModel as City,
    ClinicModel as Clinic,
    PositionModel as Position,
    ProcedureModel as Procedure,
)
from app.infrastructure.models.treatment import TreatmentModel as Treatment
from app.infrastructure.models.user import UserModel as User
from app.infrastructure.models.visit import VisitModel as Visit

__all__ = [
    "Base",
    "BaseModel",
    "SoftDeleteModel",
    "User",
    "Position",
    "Procedure",
    "Clinic",
    "City",
    "Visit",
    "Treatment",
]

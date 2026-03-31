from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from app.api.dependencies import get_current_user, get_dashboard_service
from app.application.dashboard_service import DashboardAppService
from app.domain.entities import User

router = APIRouter()


class DashboardVisit(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: str = None
    doctor: str = None
    procedure_name: str = None
    clinic_name: str = None


class DashboardTreatment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    date_start: str = None
    days: int
    status: str


class DashboardResponse(BaseModel):
    recent_visits: List[DashboardVisit]
    active_treatments: List[DashboardTreatment]
    total_visits: int
    total_treatments: int
    active_treatments_count: int
    treatment_regions: List[str]


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: DashboardAppService = Depends(get_dashboard_service),
):
    data = await service.get_dashboard(current_user.id)
    recent = [
        DashboardVisit(
            id=v.id, date=v.date.isoformat() if v.date else None,
            doctor=v.doctor,
            procedure_name=v.procedure.name if v.procedure else None,
            clinic_name=v.clinic.name if v.clinic else None,
        )
        for v in data["recent_visits"]
    ]
    active = [
        DashboardTreatment(
            id=t.id, name=t.name,
            date_start=t.date_start.isoformat() if t.date_start else None,
            days=t.days, status=t.status,
        )
        for t in data["active_treatments"]
    ]
    return DashboardResponse(
        recent_visits=recent, active_treatments=active,
        total_visits=data["total_visits"],
        total_treatments=len(data["all_treatments"]),
        active_treatments_count=len(data["active_treatments"]),
        treatment_regions=data["treatment_regions"],
    )

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from app.api.dependencies import get_current_user, get_dashboard_service
from app.application.dashboard_service import DashboardAppService
from app.domain.entities import User
from app.domain.value_objects import BODY_REGION_KEYS
from app.schemas.body_map import BodyMapSummaryResponse, BodyRegionDetailResponse

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
    )


@router.get("/body-map/", response_model=BodyMapSummaryResponse)
async def get_body_map(
    current_user: User = Depends(get_current_user),
    service: DashboardAppService = Depends(get_dashboard_service),
):
    return await service.get_body_map_summary(current_user.id)


@router.get("/body-map/{region_key}/", response_model=BodyRegionDetailResponse)
async def get_body_map_region(
    region_key: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: DashboardAppService = Depends(get_dashboard_service),
):
    if region_key not in BODY_REGION_KEYS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid region key: {region_key}")
    return await service.get_body_map_detail(current_user.id, region_key, limit, offset)

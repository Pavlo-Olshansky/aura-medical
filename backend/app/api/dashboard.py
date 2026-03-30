from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models.treatment import Treatment, KYIV_TZ
from app.models.user import User
from app.models.visit import Visit

router = APIRouter()


class DashboardVisit(BaseModel):
    id: int
    date: datetime
    doctor: str = None
    procedure_name: str = None
    clinic_name: str = None

    class Config:
        from_attributes = True


class DashboardTreatment(BaseModel):
    id: int
    name: str
    date_start: datetime
    days: int
    status: str

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    recent_visits: List[DashboardVisit]
    active_treatments: List[DashboardTreatment]
    total_visits: int
    total_treatments: int
    active_treatments_count: int


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Recent visits (last 10)
    visits_query = (
        select(Visit)
        .where(Visit.user_id == current_user.id, Visit.deleted_at.is_(None))
        .options(selectinload(Visit.procedure), selectinload(Visit.clinic))
        .order_by(Visit.date.desc())
        .limit(10)
    )
    visits_result = await session.execute(visits_query)
    visits = visits_result.scalars().all()

    recent_visits = [
        DashboardVisit(
            id=v.id,
            date=v.date,
            doctor=v.doctor,
            procedure_name=v.procedure.name if v.procedure else None,
            clinic_name=v.clinic.name if v.clinic else None,
        )
        for v in visits
    ]

    # Total visits count
    total_visits_result = await session.execute(
        select(func.count(Visit.id)).where(
            Visit.user_id == current_user.id, Visit.deleted_at.is_(None)
        )
    )
    total_visits = total_visits_result.scalar() or 0

    # All treatments
    treatments_query = select(Treatment).where(
        Treatment.user_id == current_user.id, Treatment.deleted_at.is_(None)
    )
    treatments_result = await session.execute(treatments_query)
    treatments = treatments_result.scalars().all()

    total_treatments = len(treatments)
    active_treatments = [
        DashboardTreatment(
            id=t.id, name=t.name, date_start=t.date_start, days=t.days, status=t.status
        )
        for t in treatments
        if t.status == "active"
    ]

    return DashboardResponse(
        recent_visits=recent_visits,
        active_treatments=active_treatments,
        total_visits=total_visits,
        total_treatments=total_treatments,
        active_treatments_count=len(active_treatments),
    )

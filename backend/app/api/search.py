from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel
from app.infrastructure.models.reference import (
    CityModel,
    ClinicModel,
    PositionModel,
    ProcedureModel,
)
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.vaccination import VaccinationModel
from app.infrastructure.models.visit import VisitModel
from app.schemas.search import (
    LabResultSearchItem,
    SearchGroup,
    SearchResponse,
    TreatmentSearchItem,
    VaccinationSearchItem,
    VisitSearchItem,
)

router = APIRouter()


def _icontains(column, term: str):
    """Case-insensitive contains using ICU collation — works with C locale for Cyrillic."""
    return func.lower(column.collate("und-x-icu")).like(f"%{term}%")


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    term = q.lower()

    visits = await _search_visits(session, current_user.id, term, limit)
    treatments = await _search_treatments(session, current_user.id, term, limit)
    lab_results = await _search_lab_results(session, current_user.id, term, limit)
    vaccinations = await _search_vaccinations(session, current_user.id, term, limit)

    return SearchResponse(
        visits=visits,
        treatments=treatments,
        lab_results=lab_results,
        vaccinations=vaccinations,
    )


async def _search_visits(
    session: AsyncSession, user_id: int, term: str, limit: int,
) -> SearchGroup[VisitSearchItem]:
    base_filter = [
        VisitModel.user_id == user_id,
        VisitModel.deleted_at.is_(None),
    ]
    text_filter = or_(
        _icontains(VisitModel.doctor, term),
        _icontains(VisitModel.comment, term),
        _icontains(VisitModel.procedure_details, term),
        _icontains(VisitModel.body_region, term),
        _icontains(PositionModel.name, term),
        _icontains(ProcedureModel.name, term),
        _icontains(ClinicModel.name, term),
        _icontains(CityModel.name, term),
    )

    query = (
        select(VisitModel)
        .outerjoin(PositionModel, VisitModel.position_id == PositionModel.id)
        .outerjoin(ProcedureModel, VisitModel.procedure_id == ProcedureModel.id)
        .outerjoin(ClinicModel, VisitModel.clinic_id == ClinicModel.id)
        .outerjoin(CityModel, VisitModel.city_id == CityModel.id)
        .where(*base_filter, text_filter)
        .options(
            selectinload(VisitModel.position),
            selectinload(VisitModel.procedure),
            selectinload(VisitModel.clinic),
            selectinload(VisitModel.city),
        )
        .order_by(VisitModel.date.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.scalars().unique().all()

    count_query = (
        select(func.count(VisitModel.id))
        .outerjoin(PositionModel, VisitModel.position_id == PositionModel.id)
        .outerjoin(ProcedureModel, VisitModel.procedure_id == ProcedureModel.id)
        .outerjoin(ClinicModel, VisitModel.clinic_id == ClinicModel.id)
        .outerjoin(CityModel, VisitModel.city_id == CityModel.id)
        .where(*base_filter, text_filter)
    )
    total = (await session.execute(count_query)).scalar() or 0

    items = [
        VisitSearchItem(
            id=v.id,
            date=v.date,
            doctor=v.doctor,
            position_name=v.position.name if v.position else None,
            procedure_name=v.procedure.name if v.procedure else None,
            clinic_name=v.clinic.name if v.clinic else None,
            city_name=v.city.name if v.city else None,
            body_region=v.body_region,
            comment=v.comment,
        )
        for v in rows
    ]
    return SearchGroup(items=items, total=total)


async def _search_treatments(
    session: AsyncSession, user_id: int, term: str, limit: int,
) -> SearchGroup[TreatmentSearchItem]:
    base_filter = [
        TreatmentModel.user_id == user_id,
        TreatmentModel.deleted_at.is_(None),
    ]
    text_filter = or_(
        _icontains(TreatmentModel.name, term),
        _icontains(TreatmentModel.receipt, term),
        _icontains(TreatmentModel.body_region, term),
    )

    query = (
        select(TreatmentModel)
        .where(*base_filter, text_filter)
        .order_by(TreatmentModel.date_start.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.scalars().all()

    count_query = (
        select(func.count(TreatmentModel.id))
        .where(*base_filter, text_filter)
    )
    total = (await session.execute(count_query)).scalar() or 0

    today = datetime.now().date()
    items = [
        TreatmentSearchItem(
            id=t.id,
            date_start=t.date_start,
            name=t.name,
            days=t.days,
            status="active" if (t.date_start.date() + timedelta(days=t.days)) >= today else "completed",
            body_region=t.body_region,
        )
        for t in rows
    ]
    return SearchGroup(items=items, total=total)


async def _search_lab_results(
    session: AsyncSession, user_id: int, term: str, limit: int,
) -> SearchGroup[LabResultSearchItem]:
    base_filter = [
        LabResultModel.user_id == user_id,
        LabResultModel.deleted_at.is_(None),
    ]

    matching_lab_ids_subq = (
        select(LabTestEntryModel.lab_result_id)
        .join(LabResultModel, LabTestEntryModel.lab_result_id == LabResultModel.id)
        .where(*base_filter, _icontains(LabTestEntryModel.biomarker_name, term))
    ).subquery()

    text_filter = or_(
        _icontains(LabResultModel.notes, term),
        LabResultModel.id.in_(select(matching_lab_ids_subq.c.lab_result_id)),
    )

    query = (
        select(LabResultModel)
        .where(*base_filter, text_filter)
        .options(selectinload(LabResultModel.entries))
        .order_by(LabResultModel.date.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.scalars().unique().all()

    count_query = (
        select(func.count(LabResultModel.id))
        .where(*base_filter, text_filter)
    )
    total = (await session.execute(count_query)).scalar() or 0

    items = [
        LabResultSearchItem(
            id=lr.id,
            date=lr.date,
            notes=lr.notes,
            biomarker_names=[e.biomarker_name for e in lr.entries],
            visit_id=lr.visit_id,
        )
        for lr in rows
    ]
    return SearchGroup(items=items, total=total)


async def _search_vaccinations(
    session: AsyncSession, user_id: int, term: str, limit: int,
) -> SearchGroup[VaccinationSearchItem]:
    base_filter = [
        VaccinationModel.user_id == user_id,
        VaccinationModel.deleted_at.is_(None),
    ]
    text_filter = or_(
        _icontains(VaccinationModel.vaccine_name, term),
        _icontains(VaccinationModel.manufacturer, term),
        _icontains(VaccinationModel.notes, term),
    )

    query = (
        select(VaccinationModel)
        .where(*base_filter, text_filter)
        .order_by(VaccinationModel.date.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.scalars().all()

    count_query = (
        select(func.count(VaccinationModel.id))
        .where(*base_filter, text_filter)
    )
    total = (await session.execute(count_query)).scalar() or 0

    items = [
        VaccinationSearchItem(
            id=v.id,
            date=v.date,
            vaccine_name=v.vaccine_name,
            dose_number=v.dose_number,
            manufacturer=v.manufacturer,
            notes=v.notes,
        )
        for v in rows
    ]
    return SearchGroup(items=items, total=total)

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import KYIV_TZ
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.visit import VisitModel
from app.schemas.calendar import CalendarEventResponse

# Colors
COLOR_VISIT_PAST = "#42A5F5"
COLOR_VISIT_FUTURE = "#66BB6A"
COLOR_TREATMENT = "#FFA726"


def derive_visit_label(
    procedure_name: Optional[str],
    position_name: Optional[str],
    body_region: Optional[str],
    clinic_name: Optional[str],
) -> str:
    if procedure_name and clinic_name:
        return f"{procedure_name} — {clinic_name}"
    if position_name and clinic_name:
        return f"{position_name} — {clinic_name}"
    if body_region and clinic_name:
        return f"{body_region} — {clinic_name}"
    if clinic_name:
        return clinic_name
    if procedure_name:
        return procedure_name
    if position_name:
        return position_name
    return "Візит"


class CalendarAppService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_events(
        self, user_id: int, date_from: date, date_to: date,
    ) -> list[CalendarEventResponse]:
        dt_from = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=KYIV_TZ)
        dt_to = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=KYIV_TZ)
        now = datetime.now(KYIV_TZ)

        visits = await self._fetch_visits(user_id, dt_from, dt_to)
        treatments = await self._fetch_treatments(user_id, dt_from, dt_to)

        events: list[CalendarEventResponse] = []

        for v in visits:
            proc_name = v.procedure.name if v.procedure else None
            pos_name = v.position.name if v.position else None
            clinic_name = v.clinic.name if v.clinic else None
            city_name = v.city.name if v.city else None
            is_future = v.date > now

            title = derive_visit_label(proc_name, pos_name, v.body_region, clinic_name)
            extra: dict = {}
            if proc_name:
                extra["procedure"] = proc_name
            if clinic_name:
                extra["clinic"] = clinic_name
            if v.body_region:
                extra["body_region"] = v.body_region
            if v.doctor:
                extra["doctor"] = v.doctor
            if city_name:
                extra["city"] = city_name

            events.append(CalendarEventResponse(
                id=v.id,
                event_type="visit",
                title=title,
                start=v.date,
                end=v.date + timedelta(hours=1),
                all_day=False,
                color=COLOR_VISIT_FUTURE if is_future else COLOR_VISIT_PAST,
                url=f"/visits/{v.id}",
                extra=extra,
            ))

        for t in treatments:
            end_date = t.date_start + timedelta(days=t.days)
            events.append(CalendarEventResponse(
                id=t.id,
                event_type="treatment",
                title=t.name,
                start=t.date_start,
                end=end_date,
                all_day=True,
                color=COLOR_TREATMENT,
                url=f"/treatments/{t.id}",
                extra={"body_region": t.body_region} if t.body_region else {},
            ))

        return events

    async def _fetch_visits(
        self, user_id: int, dt_from: datetime, dt_to: datetime,
    ) -> list[VisitModel]:
        result = await self._session.execute(
            select(VisitModel)
            .where(
                VisitModel.user_id == user_id,
                VisitModel.deleted_at.is_(None),
                VisitModel.date >= dt_from,
                VisitModel.date <= dt_to,
            )
            .options(
                selectinload(VisitModel.position),
                selectinload(VisitModel.procedure),
                selectinload(VisitModel.clinic),
                selectinload(VisitModel.city),
            )
            .order_by(VisitModel.date)
        )
        return list(result.scalars().all())

    async def _fetch_treatments(
        self, user_id: int, dt_from: datetime, dt_to: datetime,
    ) -> list[TreatmentModel]:
        result = await self._session.execute(
            select(TreatmentModel)
            .where(
                TreatmentModel.user_id == user_id,
                TreatmentModel.deleted_at.is_(None),
                TreatmentModel.date_start <= dt_to,
                TreatmentModel.date_start + TreatmentModel.days * timedelta(days=1) >= dt_from,
            )
            .order_by(TreatmentModel.date_start)
        )
        return list(result.scalars().all())

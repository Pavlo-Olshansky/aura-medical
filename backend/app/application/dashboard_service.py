from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import extract, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import TreatmentRepository, VisitRepository

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


class DashboardAppService:
    def __init__(
        self,
        visit_repo: VisitRepository,
        treatment_repo: TreatmentRepository,
        session: AsyncSession | None = None,
    ):
        self._visit_repo = visit_repo
        self._treatment_repo = treatment_repo
        self._session = session

    async def get_dashboard(self, user_id: int) -> dict:
        recent_visits = await self._visit_repo.list_recent(user_id, limit=10)
        total_visits = await self._visit_repo.count_total(user_id)

        all_treatments = await self._treatment_repo.list_all(user_id)
        active = [t for t in all_treatments if t.status == "active"]

        treatment_regions = list({
            t.body_region for t in active
            if t.body_region and t.body_region != "whole_body"
        })

        result = {
            "recent_visits": recent_visits,
            "total_visits": total_visits,
            "all_treatments": all_treatments,
            "active_treatments": active,
            "treatment_regions": treatment_regions,
        }

        if self._session:
            result.update(await self._get_expenses(user_id))
            result.update(await self._get_vaccination_alerts(user_id))

        return result

    async def _get_expenses(self, user_id: int) -> dict:
        from app.infrastructure.models.visit import VisitModel

        now = datetime.now(KYIV_TZ)
        current_year = now.year

        year_result = await self._session.execute(
            select(func.coalesce(func.sum(VisitModel.price), 0))
            .where(VisitModel.user_id == user_id)
            .where(VisitModel.deleted_at.is_(None))
            .where(VisitModel.price.isnot(None))
            .where(extract("year", VisitModel.date) == current_year)
        )
        expenses_year = year_result.scalar() or Decimal("0")

        total_result = await self._session.execute(
            select(func.coalesce(func.sum(VisitModel.price), 0))
            .where(VisitModel.user_id == user_id)
            .where(VisitModel.deleted_at.is_(None))
            .where(VisitModel.price.isnot(None))
        )
        expenses_total = total_result.scalar() or Decimal("0")

        return {
            "expenses_year": float(expenses_year),
            "expenses_total": float(expenses_total),
        }

    async def _get_vaccination_alerts(self, user_id: int) -> dict:
        from app.infrastructure.models.vaccination import VaccinationModel

        now = datetime.now(KYIV_TZ)

        upcoming_result = await self._session.execute(
            select(VaccinationModel)
            .where(VaccinationModel.user_id == user_id)
            .where(VaccinationModel.deleted_at.is_(None))
            .where(VaccinationModel.next_due_date.isnot(None))
            .where(VaccinationModel.next_due_date > now)
            .order_by(VaccinationModel.next_due_date)
            .limit(5)
        )
        upcoming = [
            {"id": v.id, "vaccine_name": v.vaccine_name, "next_due_date": str(v.next_due_date), "status": "upcoming"}
            for v in upcoming_result.scalars().all()
        ]

        overdue_result = await self._session.execute(
            select(VaccinationModel)
            .where(VaccinationModel.user_id == user_id)
            .where(VaccinationModel.deleted_at.is_(None))
            .where(VaccinationModel.next_due_date.isnot(None))
            .where(VaccinationModel.next_due_date <= now)
            .order_by(VaccinationModel.next_due_date.desc())
            .limit(5)
        )
        overdue = [
            {"id": v.id, "vaccine_name": v.vaccine_name, "next_due_date": str(v.next_due_date), "status": "overdue"}
            for v in overdue_result.scalars().all()
        ]

        return {
            "upcoming_vaccinations": upcoming,
            "overdue_vaccinations": overdue,
        }

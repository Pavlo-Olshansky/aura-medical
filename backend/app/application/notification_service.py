from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.models.notification import NotificationDismissalModel
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.vaccination import VaccinationModel
from app.infrastructure.models.visit import VisitModel

from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")

REMINDER_WINDOWS = {
    "day_before": timedelta(hours=24),
    "hour_before": timedelta(hours=1),
}


class NotificationAppService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_reminders(self, user_id: int) -> list[dict]:
        now = datetime.now(KYIV_TZ)
        dismissed = await self._get_dismissed(user_id)
        reminders: list[dict] = []

        reminders.extend(await self._visit_reminders(user_id, now, dismissed))
        reminders.extend(await self._treatment_reminders(user_id, now, dismissed))
        reminders.extend(await self._vaccination_reminders(user_id, now, dismissed))

        reminders.sort(key=lambda r: r["event_date"])
        return reminders

    async def dismiss(self, user_id: int, entity_type: str, entity_id: int, reminder_type: str) -> None:
        existing = await self._session.execute(
            select(NotificationDismissalModel).where(
                NotificationDismissalModel.user_id == user_id,
                NotificationDismissalModel.entity_type == entity_type,
                NotificationDismissalModel.entity_id == entity_id,
                NotificationDismissalModel.reminder_type == reminder_type,
            )
        )
        if existing.scalar_one_or_none():
            return
        self._session.add(NotificationDismissalModel(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_type=reminder_type,
        ))
        await self._session.commit()

    async def _get_dismissed(self, user_id: int) -> set[tuple[str, int, str]]:
        result = await self._session.execute(
            select(
                NotificationDismissalModel.entity_type,
                NotificationDismissalModel.entity_id,
                NotificationDismissalModel.reminder_type,
            ).where(NotificationDismissalModel.user_id == user_id)
        )
        return {(r[0], r[1], r[2]) for r in result.all()}

    async def _visit_reminders(
        self, user_id: int, now: datetime, dismissed: set
    ) -> list[dict]:
        window_start = now
        window_end = now + timedelta(hours=24)

        result = await self._session.execute(
            select(VisitModel)
            .options(selectinload(VisitModel.position), selectinload(VisitModel.procedure))
            .where(
                VisitModel.user_id == user_id,
                VisitModel.deleted_at.is_(None),
                VisitModel.date > window_start,
                VisitModel.date <= window_end,
            )
            .order_by(VisitModel.date)
        )
        visits = result.scalars().all()

        reminders = []
        for v in visits:
            title_parts = []
            if v.procedure:
                title_parts.append(v.procedure.name)
            if v.doctor:
                title_parts.append(v.doctor)
            title = " — ".join(title_parts) if title_parts else "Візит"

            for rtype, window in REMINDER_WINDOWS.items():
                if (v.date - now) <= window and ("visit", v.id, rtype) not in dismissed:
                    reminders.append(self._make_reminder(
                        entity_type="visit",
                        entity_id=v.id,
                        reminder_type=rtype,
                        title=f"Візит: {title}",
                        event_date=v.date,
                        route=f"/visits/{v.id}",
                    ))
        return reminders

    async def _treatment_reminders(
        self, user_id: int, now: datetime, dismissed: set
    ) -> list[dict]:
        window_start = now
        window_end = now + timedelta(hours=24)

        result = await self._session.execute(
            select(TreatmentModel).where(
                TreatmentModel.user_id == user_id,
                TreatmentModel.deleted_at.is_(None),
                TreatmentModel.date_start > window_start,
                TreatmentModel.date_start <= window_end,
            )
            .order_by(TreatmentModel.date_start)
        )
        treatments = result.scalars().all()

        reminders = []
        for t in treatments:
            for rtype, window in REMINDER_WINDOWS.items():
                if (t.date_start - now) <= window and ("treatment", t.id, rtype) not in dismissed:
                    reminders.append(self._make_reminder(
                        entity_type="treatment",
                        entity_id=t.id,
                        reminder_type=rtype,
                        title=f"Лікування: {t.name}",
                        event_date=t.date_start,
                        route=f"/treatments/{t.id}/edit",
                    ))
        return reminders

    async def _vaccination_reminders(
        self, user_id: int, now: datetime, dismissed: set
    ) -> list[dict]:
        window_start = now
        window_end = now + timedelta(hours=24)

        result = await self._session.execute(
            select(VaccinationModel).where(
                VaccinationModel.user_id == user_id,
                VaccinationModel.deleted_at.is_(None),
                VaccinationModel.next_due_date.isnot(None),
                VaccinationModel.next_due_date > window_start,
                VaccinationModel.next_due_date <= window_end,
            )
            .order_by(VaccinationModel.next_due_date)
        )
        vaccinations = result.scalars().all()

        reminders = []
        for v in vaccinations:
            if v.next_due_date is None:
                continue
            for rtype, window in REMINDER_WINDOWS.items():
                if (v.next_due_date - now) <= window and ("vaccination", v.id, rtype) not in dismissed:
                    reminders.append(self._make_reminder(
                        entity_type="vaccination",
                        entity_id=v.id,
                        reminder_type=rtype,
                        title=f"Вакцинація: {v.vaccine_name}",
                        event_date=v.next_due_date,
                        route=f"/vaccinations/{v.id}/edit",
                    ))
        return reminders

    @staticmethod
    def _make_reminder(
        entity_type: str,
        entity_id: int,
        reminder_type: str,
        title: str,
        event_date: datetime,
        route: str,
    ) -> dict:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reminder_type": reminder_type,
            "title": title,
            "event_date": event_date,
            "route": route,
        }

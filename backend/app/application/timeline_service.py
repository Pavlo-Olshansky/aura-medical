from __future__ import annotations
import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.infrastructure.repositories.lab_result_repository import SqlAlchemyLabResultRepository
from app.infrastructure.repositories.treatment_repository import SqlAlchemyTreatmentRepository
from app.infrastructure.repositories.vaccination_repository import SqlAlchemyVaccinationRepository
from app.infrastructure.repositories.visit_repository import SqlAlchemyVisitRepository


@dataclass
class TimelineEvent:
    id: int
    event_type: str  # "visit" | "treatment" | "lab_result" | "vaccination"
    date: datetime
    title: str
    subtitle: Optional[str] = None
    entity_id: Optional[int] = None


class TimelineAppService:
    def __init__(
        self,
        visit_repo: SqlAlchemyVisitRepository,
        treatment_repo: SqlAlchemyTreatmentRepository,
        lab_result_repo: SqlAlchemyLabResultRepository,
        vaccination_repo: SqlAlchemyVaccinationRepository,
    ):
        self._visit_repo = visit_repo
        self._treatment_repo = treatment_repo
        self._lab_result_repo = lab_result_repo
        self._vaccination_repo = vaccination_repo

    async def list(
        self,
        user_id: int,
        event_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[TimelineEvent], int]:
        tasks = []
        types_to_fetch = []

        if event_type is None or event_type == "visit":
            types_to_fetch.append("visit")
            tasks.append(self._fetch_visits(user_id, date_from, date_to))
        if event_type is None or event_type == "treatment":
            types_to_fetch.append("treatment")
            tasks.append(self._fetch_treatments(user_id, date_from, date_to))
        if event_type is None or event_type == "lab_result":
            types_to_fetch.append("lab_result")
            tasks.append(self._fetch_lab_results(user_id, date_from, date_to))
        if event_type is None or event_type == "vaccination":
            types_to_fetch.append("vaccination")
            tasks.append(self._fetch_vaccinations(user_id, date_from, date_to))

        all_events: list[TimelineEvent] = []
        for task in tasks:
            events = await task
            all_events.extend(events)

        all_events.sort(key=lambda e: e.date, reverse=True)

        total = len(all_events)
        start = (page - 1) * size
        page_items = all_events[start:start + size]

        return page_items, total

    async def _fetch_visits(self, user_id: int, date_from: Optional[date], date_to: Optional[date]) -> list[TimelineEvent]:
        filters = {}
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        visits, _ = await self._visit_repo.list(user_id, filters, "-date", 1, 1000)
        events = []
        for v in visits:
            procedure_name = v.procedure.name if v.procedure else None
            clinic_name = v.clinic.name if v.clinic else None
            title = f"Візит: {procedure_name}" if procedure_name else "Візит"
            subtitle_parts = []
            if v.doctor:
                subtitle_parts.append(v.doctor)
            if clinic_name:
                subtitle_parts.append(clinic_name)
            subtitle = ", ".join(subtitle_parts) if subtitle_parts else None
            events.append(TimelineEvent(
                id=v.id, event_type="visit", date=v.date,
                title=title, subtitle=subtitle, entity_id=v.id,
            ))
        return events

    async def _fetch_treatments(self, user_id: int, date_from: Optional[date], date_to: Optional[date]) -> list[TimelineEvent]:
        all_treatments = await self._treatment_repo.list_all(user_id)
        events = []
        for t in all_treatments:
            if date_from and t.date_start.date() < date_from:
                continue
            if date_to and t.date_start.date() > date_to:
                continue
            status_label = "активне" if t.status == "active" else "завершене"
            title = f"Лікування: {t.name}"
            subtitle = f"{t.days} дн., {status_label}"
            events.append(TimelineEvent(
                id=t.id, event_type="treatment", date=t.date_start,
                title=title, subtitle=subtitle, entity_id=t.id,
            ))
        return events

    async def _fetch_lab_results(self, user_id: int, date_from: Optional[date], date_to: Optional[date]) -> list[TimelineEvent]:
        results, _ = await self._lab_result_repo.list(user_id, date_from=date_from, date_to=date_to, sort="-date", page=1, size=1000)
        events = []
        for lr in results:
            entries_count = len(lr.entries) if lr.entries else 0
            out_of_range = sum(1 for e in (lr.entries or []) if e.is_normal is False)
            title = f"Аналізи ({entries_count} показників)"
            subtitle = f"{out_of_range} поза нормою" if out_of_range > 0 else "Всі в нормі"
            events.append(TimelineEvent(
                id=lr.id, event_type="lab_result", date=lr.date,
                title=title, subtitle=subtitle, entity_id=lr.id,
            ))
        return events

    async def _fetch_vaccinations(self, user_id: int, date_from: Optional[date], date_to: Optional[date]) -> list[TimelineEvent]:
        vaccinations, _ = await self._vaccination_repo.list(user_id, sort="-date", page=1, size=1000)
        events = []
        for v in vaccinations:
            if date_from and v.date.date() < date_from:
                continue
            if date_to and v.date.date() > date_to:
                continue
            title = f"Вакцинація: {v.vaccine_name}"
            subtitle = f"Доза {v.dose_number}"
            if v.manufacturer:
                subtitle += f", {v.manufacturer}"
            events.append(TimelineEvent(
                id=v.id, event_type="vaccination", date=v.date,
                title=title, subtitle=subtitle, entity_id=v.id,
            ))
        return events

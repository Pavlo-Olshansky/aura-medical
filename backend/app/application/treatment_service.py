from __future__ import annotations
import math
from typing import Optional

from app.application.commands import CreateTreatmentCommand, UpdateTreatmentCommand
from app.application.update_utils import apply_update
from app.domain.entities import Treatment
from app.domain.exceptions import EntityNotFound
from app.domain.repositories import TreatmentRepository


class TreatmentAppService:
    def __init__(self, repo: TreatmentRepository):
        self._repo = repo

    async def get(self, treatment_id: int, user_id: int) -> Treatment:
        treatment = await self._repo.get_by_id(treatment_id, user_id)
        if not treatment:
            raise EntityNotFound("Treatment not found")
        return treatment

    async def list(self, user_id: int, status_filter: Optional[str], sort: str, page: int, size: int) -> tuple[list[Treatment], int]:
        all_treatments = await self._repo.list_all(user_id)

        desc = sort.startswith("-")
        sort_field = sort.lstrip("-")
        all_treatments.sort(key=lambda t: getattr(t, sort_field, t.date_start), reverse=desc)

        if status_filter in ("active", "completed"):
            all_treatments = [t for t in all_treatments if t.status == status_filter]

        total = len(all_treatments)
        start = (page - 1) * size
        page_items = all_treatments[start:start + size]
        pages = math.ceil(total / size) if total > 0 else 1

        return page_items, total

    async def create(self, user_id: int, cmd: CreateTreatmentCommand) -> Treatment:
        treatment = Treatment(
            user_id=user_id, date_start=cmd.date_start,
            name=cmd.name, days=cmd.days, receipt=cmd.receipt,
            body_region=cmd.body_region,
        )
        return await self._repo.save(treatment)

    async def update(self, treatment_id: int, user_id: int, cmd: UpdateTreatmentCommand) -> Treatment:
        treatment = await self.get(treatment_id, user_id)
        apply_update(treatment, cmd)
        return await self._repo.save(treatment)

    async def delete(self, treatment_id: int, user_id: int) -> None:
        treatment = await self.get(treatment_id, user_id)
        treatment.soft_delete()
        await self._repo.save(treatment)

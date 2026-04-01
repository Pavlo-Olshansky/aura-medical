from __future__ import annotations
from datetime import date
from typing import Optional

from app.application.commands import CreateLabResultCommand, UpdateLabResultCommand
from app.domain.entities import LabResult, LabTestEntry
from app.domain.exceptions import EntityNotFound
from app.infrastructure.repositories.lab_result_repository import SqlAlchemyLabResultRepository


class LabResultAppService:
    def __init__(self, repo: SqlAlchemyLabResultRepository):
        self._repo = repo

    async def get(self, lab_result_id: int, user_id: int) -> LabResult:
        result = await self._repo.get_by_id(lab_result_id, user_id)
        if not result:
            raise EntityNotFound("Lab result not found")
        return result

    async def list(
        self,
        user_id: int,
        visit_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort: str = "-date",
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[LabResult], int]:
        return await self._repo.list(user_id, visit_id, date_from, date_to, sort, page, size)

    async def create(self, user_id: int, cmd: CreateLabResultCommand) -> LabResult:
        entries = [
            LabTestEntry(
                biomarker_id=e.biomarker_id,
                biomarker_name=e.biomarker_name,
                value=e.value,
                unit=e.unit,
                ref_min=e.ref_min,
                ref_max=e.ref_max,
            )
            for e in cmd.entries
        ]
        lab_result = LabResult(
            user_id=user_id,
            visit_id=cmd.visit_id,
            date=cmd.date,
            notes=cmd.notes,
            entries=entries,
        )
        return await self._repo.save(lab_result)

    async def update(self, lab_result_id: int, user_id: int, cmd: UpdateLabResultCommand) -> LabResult:
        lab_result = await self.get(lab_result_id, user_id)
        if cmd.date is not None: lab_result.date = cmd.date
        if cmd.visit_id is not None: lab_result.visit_id = cmd.visit_id
        if cmd.notes is not None: lab_result.notes = cmd.notes
        if cmd.entries is not None:
            lab_result.entries = [
                LabTestEntry(
                    biomarker_id=e.biomarker_id,
                    biomarker_name=e.biomarker_name,
                    value=e.value,
                    unit=e.unit,
                    ref_min=e.ref_min,
                    ref_max=e.ref_max,
                )
                for e in cmd.entries
            ]
        return await self._repo.save(lab_result)

    async def delete(self, lab_result_id: int, user_id: int) -> None:
        lab_result = await self.get(lab_result_id, user_id)
        lab_result.soft_delete()
        await self._repo.save(lab_result)

    async def biomarker_trend(self, user_id: int, biomarker_name: str) -> list[dict]:
        return await self._repo.biomarker_trend(user_id, biomarker_name)

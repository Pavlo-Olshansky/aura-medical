from __future__ import annotations
from typing import Optional

from app.application.commands import CreateMetricTypeCommand, UpdateMetricTypeCommand
from app.domain.entities import MetricType
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.infrastructure.repositories.metric_type_repository import SqlAlchemyMetricTypeRepository


class MetricTypeAppService:
    def __init__(self, repo: SqlAlchemyMetricTypeRepository):
        self._repo = repo

    async def list_all(self, search: Optional[str] = None) -> list[MetricType]:
        return await self._repo.list_all(search)

    async def create(self, cmd: CreateMetricTypeCommand) -> MetricType:
        ref = MetricType(
            name=cmd.name, unit=cmd.unit,
            has_secondary_value=cmd.has_secondary_value,
            ref_min=cmd.ref_min, ref_max=cmd.ref_max,
            ref_min_secondary=cmd.ref_min_secondary,
            ref_max_secondary=cmd.ref_max_secondary,
            sort_order=cmd.sort_order,
        )
        return await self._repo.save(ref)

    async def update(self, ref_id: int, cmd: UpdateMetricTypeCommand) -> MetricType:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Metric type not found")
        if cmd.name is not None: ref.name = cmd.name
        if cmd.unit is not None: ref.unit = cmd.unit
        if cmd.has_secondary_value is not None: ref.has_secondary_value = cmd.has_secondary_value
        if cmd.ref_min is not None: ref.ref_min = cmd.ref_min
        if cmd.ref_max is not None: ref.ref_max = cmd.ref_max
        if cmd.ref_min_secondary is not None: ref.ref_min_secondary = cmd.ref_min_secondary
        if cmd.ref_max_secondary is not None: ref.ref_max_secondary = cmd.ref_max_secondary
        if cmd.sort_order is not None: ref.sort_order = cmd.sort_order
        return await self._repo.save(ref)

    async def delete(self, ref_id: int) -> None:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Metric type not found")
        if await self._repo.is_referenced(ref_id):
            raise ReferenceInUse("Cannot delete — referenced by health metrics")
        await self._repo.delete(ref_id)

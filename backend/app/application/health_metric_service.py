from __future__ import annotations
from datetime import date
from typing import Optional

from app.application.commands import CreateHealthMetricCommand, UpdateHealthMetricCommand
from app.application.update_utils import apply_update
from app.domain.entities import HealthMetric
from app.domain.exceptions import DomainError, EntityNotFound
from app.infrastructure.repositories.health_metric_repository import SqlAlchemyHealthMetricRepository
from app.infrastructure.repositories.metric_type_repository import SqlAlchemyMetricTypeRepository


class HealthMetricAppService:
    def __init__(
        self,
        repo: SqlAlchemyHealthMetricRepository,
        metric_type_repo: SqlAlchemyMetricTypeRepository,
    ):
        self._repo = repo
        self._metric_type_repo = metric_type_repo

    async def get(self, metric_id: int, user_id: int) -> HealthMetric:
        metric = await self._repo.get_by_id(metric_id, user_id)
        if not metric:
            raise EntityNotFound("Health metric not found")
        return metric

    async def list(
        self,
        user_id: int,
        metric_type_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort: str = "-date",
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[HealthMetric], int]:
        return await self._repo.list(user_id, metric_type_id, date_from, date_to, sort, page, size)

    async def create(self, user_id: int, cmd: CreateHealthMetricCommand) -> HealthMetric:
        await self._validate_metric_type(cmd.metric_type_id, cmd.secondary_value)
        metric = HealthMetric(
            user_id=user_id,
            metric_type_id=cmd.metric_type_id,
            date=cmd.date,
            value=cmd.value,
            secondary_value=cmd.secondary_value,
            notes=cmd.notes,
        )
        return await self._repo.save(metric)

    async def update(self, metric_id: int, user_id: int, cmd: UpdateHealthMetricCommand) -> HealthMetric:
        metric = await self.get(metric_id, user_id)
        apply_update(metric, cmd)

        mt_id = cmd.metric_type_id if cmd.metric_type_id is not None else metric.metric_type_id
        sec_val = cmd.secondary_value if cmd.secondary_value is not None else metric.secondary_value
        await self._validate_metric_type(mt_id, sec_val)

        return await self._repo.save(metric)

    async def delete(self, metric_id: int, user_id: int) -> None:
        await self.get(metric_id, user_id)
        await self._repo.delete(metric_id, user_id)

    async def get_metric_type(self, metric_type_id: int):
        return await self._metric_type_repo.get_by_id(metric_type_id)

    async def trend(
        self,
        user_id: int,
        metric_type_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[dict]:
        return await self._repo.trend(user_id, metric_type_id, date_from, date_to)

    async def _validate_metric_type(self, metric_type_id: int, secondary_value=None) -> None:
        mt = await self._metric_type_repo.get_by_id(metric_type_id)
        if not mt:
            raise EntityNotFound("Metric type not found")
        if mt.has_secondary_value and secondary_value is None:
            raise DomainError("Secondary value is required for this metric type")

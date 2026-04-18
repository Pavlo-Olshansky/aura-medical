from __future__ import annotations

import builtins
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.entities import HealthMetric, MetricType
from app.infrastructure.models.health_metric import HealthMetricModel
from app.infrastructure.repositories.base_repository import (
    BaseQueryRepository,
    normalize_date_to_datetime,
)


class SqlAlchemyHealthMetricRepository(BaseQueryRepository[HealthMetricModel, HealthMetric]):
    model_class = HealthMetricModel

    _load_options = [
        selectinload(HealthMetricModel.metric_type),
    ]

    async def get_by_id(self, metric_id: int, user_id: int) -> Optional[HealthMetric]:
        result = await self._session.execute(
            self._base_query()
            .where(HealthMetricModel.id == metric_id, HealthMetricModel.user_id == user_id)
            .options(*self._load_options)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        user_id: int,
        metric_type_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort: str = "-date",
        page: int = 1,
        size: int = 20,
    ) -> tuple[builtins.list[HealthMetric], int]:
        query = (
            self._base_query()
            .where(HealthMetricModel.user_id == user_id)
            .options(*self._load_options)
        )
        count_query = (
            self._base_count()
            .where(HealthMetricModel.user_id == user_id)
        )

        if metric_type_id is not None:
            query = query.where(HealthMetricModel.metric_type_id == metric_type_id)
            count_query = count_query.where(HealthMetricModel.metric_type_id == metric_type_id)

        query, count_query = self._apply_date_filter(
            query, count_query, HealthMetricModel.date, date_from, date_to,
        )

        sort_map = {
            "date": HealthMetricModel.date,
            "-date": HealthMetricModel.date.desc(),
            "created": HealthMetricModel.created,
            "-created": HealthMetricModel.created.desc(),
        }
        query = self._apply_sort(query, sort, sort_map)

        total = (await self._session.execute(count_query)).scalar() or 0
        query = self._apply_pagination(query, page, size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, metric: HealthMetric) -> HealthMetric:
        if metric.id:
            model = await self._session.get(HealthMetricModel, metric.id)
            assert model is not None
            for attr in ("metric_type_id", "date", "value", "secondary_value", "notes"):
                setattr(model, attr, getattr(metric, attr))
        else:
            model = HealthMetricModel(
                user_id=metric.user_id,
                metric_type_id=metric.metric_type_id,
                date=metric.date,
                value=metric.value,
                secondary_value=metric.secondary_value,
                notes=metric.notes,
            )
        model = await self._save_and_refresh(model, refresh_attrs=["metric_type"])
        return self._to_entity(model)

    async def delete(self, metric_id: int, user_id: int) -> None:
        from sqlalchemy import delete as sa_delete
        await self._session.execute(
            sa_delete(HealthMetricModel).where(
                HealthMetricModel.id == metric_id,
                HealthMetricModel.user_id == user_id,
            )
        )
        await self._session.commit()

    async def trend(
        self,
        user_id: int,
        metric_type_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> builtins.list[dict]:
        query = (
            select(
                HealthMetricModel.date,
                HealthMetricModel.value,
                HealthMetricModel.secondary_value,
            )
            .where(
                HealthMetricModel.user_id == user_id,
                HealthMetricModel.metric_type_id == metric_type_id,
                HealthMetricModel.deleted_at.is_(None),
            )
        )
        if date_from:
            query = query.where(HealthMetricModel.date >= normalize_date_to_datetime(date_from, end=False))
        if date_to:
            query = query.where(HealthMetricModel.date <= normalize_date_to_datetime(date_to, end=True))

        query = query.order_by(HealthMetricModel.date)
        result = await self._session.execute(query)
        return [
            {
                "date": row.date,
                "value": row.value,
                "secondary_value": row.secondary_value,
            }
            for row in result.all()
        ]

    @staticmethod
    def _to_entity(model: HealthMetricModel) -> HealthMetric:
        metric_type = None
        if model.metric_type:
            metric_type = MetricType(
                id=model.metric_type.id,
                name=model.metric_type.name,
                unit=model.metric_type.unit,
                has_secondary_value=model.metric_type.has_secondary_value,
                ref_min=model.metric_type.ref_min,
                ref_max=model.metric_type.ref_max,
                ref_min_secondary=model.metric_type.ref_min_secondary,
                ref_max_secondary=model.metric_type.ref_max_secondary,
                sort_order=model.metric_type.sort_order,
                created=model.metric_type.created,
                updated=model.metric_type.updated,
            )
        return HealthMetric(
            id=model.id,
            user_id=model.user_id,
            metric_type_id=model.metric_type_id,
            date=model.date,
            value=model.value,
            secondary_value=model.secondary_value,
            notes=model.notes,
            created=model.created,
            updated=model.updated,
            metric_type=metric_type,
        )

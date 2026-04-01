from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import HealthMetric, MetricType
from app.infrastructure.models.health_metric import HealthMetricModel
from app.infrastructure.models.metric_type import MetricTypeModel


class SqlAlchemyHealthMetricRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, metric_id: int, user_id: int) -> Optional[HealthMetric]:
        result = await self._session.execute(
            select(HealthMetricModel)
            .where(HealthMetricModel.id == metric_id, HealthMetricModel.user_id == user_id)
            .options(selectinload(HealthMetricModel.metric_type))
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
    ) -> tuple[list[HealthMetric], int]:
        query = (
            select(HealthMetricModel)
            .where(HealthMetricModel.user_id == user_id)
            .options(selectinload(HealthMetricModel.metric_type))
        )
        count_query = (
            select(func.count()).select_from(HealthMetricModel)
            .where(HealthMetricModel.user_id == user_id)
        )

        if metric_type_id is not None:
            query = query.where(HealthMetricModel.metric_type_id == metric_type_id)
            count_query = count_query.where(HealthMetricModel.metric_type_id == metric_type_id)
        if date_from:
            dt = datetime.combine(date_from, datetime.min.time()) if isinstance(date_from, date) and not isinstance(date_from, datetime) else date_from
            query = query.where(HealthMetricModel.date >= dt)
            count_query = count_query.where(HealthMetricModel.date >= dt)
        if date_to:
            dt = datetime.combine(date_to, datetime.max.time()) if isinstance(date_to, date) and not isinstance(date_to, datetime) else date_to
            query = query.where(HealthMetricModel.date <= dt)
            count_query = count_query.where(HealthMetricModel.date <= dt)

        sort_map = {
            "date": HealthMetricModel.date,
            "-date": HealthMetricModel.date.desc(),
            "created": HealthMetricModel.created,
            "-created": HealthMetricModel.created.desc(),
        }
        query = query.order_by(sort_map.get(sort, HealthMetricModel.date.desc()))

        total = (await self._session.execute(count_query)).scalar() or 0
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, metric: HealthMetric) -> HealthMetric:
        if metric.id:
            model = await self._session.get(HealthMetricModel, metric.id)
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
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        # Re-fetch with eager loaded metric_type
        result = await self._session.execute(
            select(HealthMetricModel)
            .where(HealthMetricModel.id == model.id)
            .options(selectinload(HealthMetricModel.metric_type))
        )
        model = result.scalar_one()
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
    ) -> list[dict]:
        query = (
            select(
                HealthMetricModel.date,
                HealthMetricModel.value,
                HealthMetricModel.secondary_value,
            )
            .where(
                HealthMetricModel.user_id == user_id,
                HealthMetricModel.metric_type_id == metric_type_id,
            )
        )
        if date_from:
            dt = datetime.combine(date_from, datetime.min.time()) if isinstance(date_from, date) and not isinstance(date_from, datetime) else date_from
            query = query.where(HealthMetricModel.date >= dt)
        if date_to:
            dt = datetime.combine(date_to, datetime.max.time()) if isinstance(date_to, date) and not isinstance(date_to, datetime) else date_to
            query = query.where(HealthMetricModel.date <= dt)

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

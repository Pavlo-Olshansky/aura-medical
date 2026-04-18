from __future__ import annotations
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import MetricType
from app.infrastructure.models.health_metric import HealthMetricModel
from app.infrastructure.models.metric_type import MetricTypeModel


class SqlAlchemyMetricTypeRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, ref_id: int) -> Optional[MetricType]:
        result = await self._session.execute(
            select(MetricTypeModel).where(MetricTypeModel.id == ref_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, search: Optional[str] = None) -> list[MetricType]:
        query = select(MetricTypeModel)
        if search:
            query = query.where(MetricTypeModel.name.ilike(f"%{search}%"))
        query = query.order_by(MetricTypeModel.sort_order, MetricTypeModel.name)
        result = await self._session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, ref: MetricType) -> MetricType:
        if ref.id:
            model = await self._session.get(MetricTypeModel, ref.id)
            assert model is not None
            for attr in ("name", "unit", "has_secondary_value",
                         "ref_min", "ref_max", "ref_min_secondary",
                         "ref_max_secondary", "sort_order"):
                setattr(model, attr, getattr(ref, attr))
        else:
            model = MetricTypeModel(
                name=ref.name, unit=ref.unit,
                has_secondary_value=ref.has_secondary_value,
                ref_min=ref.ref_min, ref_max=ref.ref_max,
                ref_min_secondary=ref.ref_min_secondary,
                ref_max_secondary=ref.ref_max_secondary,
                sort_order=ref.sort_order,
            )
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, ref_id: int) -> None:
        from sqlalchemy import delete as sa_delete
        await self._session.execute(
            sa_delete(MetricTypeModel).where(MetricTypeModel.id == ref_id)
        )
        await self._session.commit()

    async def reference_count(self, ref_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(HealthMetricModel)
            .where(HealthMetricModel.metric_type_id == ref_id)
        )
        return result.scalar() or 0

    async def is_referenced(self, ref_id: int) -> bool:
        return (await self.reference_count(ref_id)) > 0

    @staticmethod
    def _to_entity(model: MetricTypeModel) -> MetricType:
        return MetricType(
            id=model.id, name=model.name, unit=model.unit,
            has_secondary_value=model.has_secondary_value,
            ref_min=model.ref_min, ref_max=model.ref_max,
            ref_min_secondary=model.ref_min_secondary,
            ref_max_secondary=model.ref_max_secondary,
            sort_order=model.sort_order,
            created=model.created, updated=model.updated,
        )

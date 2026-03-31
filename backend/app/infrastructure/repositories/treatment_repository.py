from __future__ import annotations
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Treatment
from app.infrastructure.models.treatment import TreatmentModel


class SqlAlchemyTreatmentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, treatment_id: int, user_id: int) -> Optional[Treatment]:
        result = await self._session.execute(
            select(TreatmentModel).where(
                TreatmentModel.id == treatment_id,
                TreatmentModel.user_id == user_id,
                TreatmentModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, user_id: int) -> list[Treatment]:
        result = await self._session.execute(
            select(TreatmentModel).where(
                TreatmentModel.user_id == user_id,
                TreatmentModel.deleted_at.is_(None),
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_region(self, user_id: int, region: str) -> list[Treatment]:
        result = await self._session.execute(
            select(TreatmentModel).where(
                TreatmentModel.user_id == user_id,
                TreatmentModel.deleted_at.is_(None),
                TreatmentModel.body_region == region,
            ).order_by(TreatmentModel.date_start.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, treatment: Treatment) -> Treatment:
        if treatment.id:
            model = await self._session.get(TreatmentModel, treatment.id)
            for attr in ("date_start", "name", "days", "receipt", "body_region", "deleted_at"):
                setattr(model, attr, getattr(treatment, attr))
        else:
            model = TreatmentModel(
                user_id=treatment.user_id, date_start=treatment.date_start,
                name=treatment.name, days=treatment.days, receipt=treatment.receipt,
                body_region=treatment.body_region,
            )
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: TreatmentModel) -> Treatment:
        return Treatment(
            id=model.id, user_id=model.user_id, date_start=model.date_start,
            name=model.name, days=model.days, receipt=model.receipt,
            body_region=model.body_region, deleted_at=model.deleted_at,
            created=model.created, updated=model.updated,
        )

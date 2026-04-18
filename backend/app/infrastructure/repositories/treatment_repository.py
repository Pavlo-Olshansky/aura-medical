from __future__ import annotations
from typing import Optional

from app.domain.entities import Treatment
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.repositories.base_repository import BaseQueryRepository


class SqlAlchemyTreatmentRepository(BaseQueryRepository[TreatmentModel, Treatment]):
    model_class = TreatmentModel

    async def get_by_id(self, treatment_id: int, user_id: int) -> Optional[Treatment]:
        result = await self._session.execute(
            self._base_query().where(
                TreatmentModel.id == treatment_id,
                TreatmentModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, user_id: int) -> list[Treatment]:
        result = await self._session.execute(
            self._base_query().where(
                TreatmentModel.user_id == user_id,
            )
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, treatment: Treatment) -> Treatment:
        if treatment.id:
            model = await self._session.get(TreatmentModel, treatment.id)
            assert model is not None
            for attr in ("date_start", "name", "days", "receipt", "body_region", "deleted_at"):
                setattr(model, attr, getattr(treatment, attr))
        else:
            model = TreatmentModel(
                user_id=treatment.user_id, date_start=treatment.date_start,
                name=treatment.name, days=treatment.days, receipt=treatment.receipt,
                body_region=treatment.body_region,
            )
        model = await self._save_and_refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: TreatmentModel) -> Treatment:
        return Treatment(
            id=model.id, user_id=model.user_id, date_start=model.date_start,
            name=model.name, days=model.days, receipt=model.receipt,
            body_region=model.body_region, deleted_at=model.deleted_at,
            created=model.created, updated=model.updated,
        )

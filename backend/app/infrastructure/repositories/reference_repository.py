from typing import Optional, Type

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Reference
from app.infrastructure.models.base import BaseModel
from app.infrastructure.models.visit import VisitModel


class SqlAlchemyReferenceRepository:
    def __init__(self, session: AsyncSession, model_class: Type[BaseModel], visit_fk_name: str):
        self._session = session
        self._model_class = model_class
        self._visit_fk_name = visit_fk_name

    async def get_by_id(self, ref_id: int) -> Optional[Reference]:
        result = await self._session.execute(
            select(self._model_class).where(self._model_class.id == ref_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[Reference]:
        result = await self._session.execute(
            select(self._model_class).order_by(self._model_class.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, ref: Reference) -> Reference:
        if ref.id:
            model = await self._session.get(self._model_class, ref.id)
            model.name = ref.name
        else:
            model = self._model_class(name=ref.name)
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def is_referenced(self, ref_id: int) -> bool:
        fk_column = getattr(VisitModel, self._visit_fk_name)
        result = await self._session.execute(
            select(func.count()).select_from(VisitModel)
            .where(fk_column == ref_id, VisitModel.deleted_at.is_(None))
        )
        return (result.scalar() or 0) > 0

    @staticmethod
    def _to_entity(model) -> Reference:
        return Reference(
            id=model.id, name=model.name,
            created=model.created, updated=model.updated,
        )

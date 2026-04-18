from __future__ import annotations
from typing import Optional, Type

from sqlalchemy import func, select
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

    async def list_all(self, sort_by_recent: bool = False, user_id: int | None = None) -> list[Reference]:
        if sort_by_recent and user_id is not None:
            fk_column = getattr(VisitModel, self._visit_fk_name)
            stmt = (
                select(self._model_class, func.max(VisitModel.date).label("last_used"))
                .outerjoin(
                    VisitModel,
                    (fk_column == self._model_class.id)
                    & (VisitModel.user_id == user_id)
                    & (VisitModel.deleted_at.is_(None)),
                )
                .group_by(self._model_class.id)
                .order_by(func.max(VisitModel.date).desc().nulls_last(), self._model_class.name)  # type: ignore[attr-defined]
            )
            result = await self._session.execute(stmt)
            return [self._to_entity(row[0]) for row in result.all()]
        result = await self._session.execute(
            select(self._model_class).order_by(self._model_class.name)  # type: ignore[attr-defined, arg-type]
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, ref: Reference) -> Reference:
        if ref.id:
            model = await self._session.get(self._model_class, ref.id)
            assert model is not None
            model.name = ref.name  # type: ignore[attr-defined]
        else:
            model = self._model_class(name=ref.name)
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def is_referenced(self, ref_id: int) -> bool:
        return (await self.reference_count(ref_id)) > 0

    async def reference_count(self, ref_id: int) -> int:
        fk_column = getattr(VisitModel, self._visit_fk_name)
        result = await self._session.execute(
            select(func.count()).select_from(VisitModel)
            .where(fk_column == ref_id, VisitModel.deleted_at.is_(None))
        )
        return result.scalar() or 0

    async def delete(self, ref_id: int) -> None:
        from sqlalchemy import delete as sa_delete
        await self._session.execute(sa_delete(self._model_class).where(self._model_class.id == ref_id))
        await self._session.commit()

    @staticmethod
    def _to_entity(model) -> Reference:
        return Reference(
            id=model.id, name=model.name,
            created=model.created, updated=model.updated,
        )

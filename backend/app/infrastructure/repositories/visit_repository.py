from __future__ import annotations

import builtins
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.domain.entities import Reference, Visit
from app.infrastructure.models.visit import VisitModel
from app.infrastructure.repositories.base_repository import BaseQueryRepository


class SqlAlchemyVisitRepository(BaseQueryRepository[VisitModel, Visit]):
    model_class = VisitModel

    _load_options = [
        selectinload(VisitModel.position),
        selectinload(VisitModel.procedure),
        selectinload(VisitModel.clinic),
        selectinload(VisitModel.city),
    ]

    async def get_by_id(self, visit_id: int, user_id: int) -> Optional[Visit]:
        result = await self._session.execute(
            self._base_query()
            .where(VisitModel.id == visit_id, VisitModel.user_id == user_id)
            .options(*self._load_options)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, user_id: int, filters: dict, sort: str, page: int, size: int) -> tuple[builtins.list[Visit], int]:
        query = (
            self._base_query()
            .where(VisitModel.user_id == user_id)
            .options(*self._load_options)
        )
        count_query = (
            self._base_count()
            .where(VisitModel.user_id == user_id)
        )

        query, count_query = self._apply_date_filter(
            query, count_query, VisitModel.date,
            filters.get("date_from"), filters.get("date_to"),
        )

        for fk in ("clinic_id", "city_id", "procedure_id", "position_id"):
            val = filters.get(fk)
            if val:
                query = query.where(getattr(VisitModel, fk) == val)
                count_query = count_query.where(getattr(VisitModel, fk) == val)
        body_region = filters.get("body_region")
        if body_region:
            query = query.where(VisitModel.body_region == body_region)
            count_query = count_query.where(VisitModel.body_region == body_region)

        sort_map = {
            "date": VisitModel.date, "-date": VisitModel.date.desc(),
            "created": VisitModel.created, "-created": VisitModel.created.desc(),
        }
        query = self._apply_sort(query, sort, sort_map)

        total = (await self._session.execute(count_query)).scalar() or 0
        query = self._apply_pagination(query, page, size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, visit: Visit) -> Visit:
        if visit.id:
            model = await self._session.get(VisitModel, visit.id)
            assert model is not None
            for attr in ("date", "position_id", "doctor", "procedure_id", "procedure_details",
                         "clinic_id", "city_id", "document", "link", "comment", "body_region", "price", "deleted_at"):
                setattr(model, attr, getattr(visit, attr))
        else:
            model = VisitModel(
                user_id=visit.user_id, date=visit.date, position_id=visit.position_id,
                doctor=visit.doctor, procedure_id=visit.procedure_id,
                procedure_details=visit.procedure_details, clinic_id=visit.clinic_id,
                city_id=visit.city_id, document=visit.document, link=visit.link,
                comment=visit.comment, body_region=visit.body_region, price=visit.price,
            )
        model = await self._save_and_refresh(
            model,
            refresh_attrs=["position", "procedure", "clinic", "city"],
        )
        return self._to_entity(model)

    async def count_total(self, user_id: int) -> int:
        result = await self._session.execute(
            self._base_count()
            .where(VisitModel.user_id == user_id)
        )
        return result.scalar() or 0

    async def list_recent(self, user_id: int, limit: int = 10) -> builtins.list[Visit]:
        result = await self._session.execute(
            self._base_query()
            .where(VisitModel.user_id == user_id)
            .options(selectinload(VisitModel.procedure), selectinload(VisitModel.clinic))
            .order_by(VisitModel.date.desc()).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: VisitModel) -> Visit:
        return Visit(
            id=model.id, user_id=model.user_id, date=model.date,
            position_id=model.position_id, doctor=model.doctor,
            procedure_id=model.procedure_id, procedure_details=model.procedure_details,
            clinic_id=model.clinic_id, city_id=model.city_id,
            document=model.document, link=model.link, comment=model.comment,
            body_region=model.body_region, price=model.price, deleted_at=model.deleted_at,
            created=model.created, updated=model.updated,
            position=Reference(id=model.position.id, name=model.position.name) if model.position else None,
            procedure=Reference(id=model.procedure.id, name=model.procedure.name) if model.procedure else None,
            clinic=Reference(id=model.clinic.id, name=model.clinic.name) if model.clinic else None,
            city=Reference(id=model.city.id, name=model.city.name) if model.city else None,
        )

from __future__ import annotations
import math
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import Reference, Visit
from app.infrastructure.models.visit import VisitModel


class SqlAlchemyVisitRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, visit_id: int, user_id: int) -> Optional[Visit]:
        result = await self._session.execute(
            select(VisitModel)
            .where(VisitModel.id == visit_id, VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None))
            .options(
                selectinload(VisitModel.position),
                selectinload(VisitModel.procedure),
                selectinload(VisitModel.clinic),
                selectinload(VisitModel.city),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(self, user_id: int, filters: dict, sort: str, page: int, size: int) -> tuple[list[Visit], int]:
        query = (
            select(VisitModel)
            .where(VisitModel.deleted_at.is_(None), VisitModel.user_id == user_id)
            .options(
                selectinload(VisitModel.position),
                selectinload(VisitModel.procedure),
                selectinload(VisitModel.clinic),
                selectinload(VisitModel.city),
            )
        )
        count_query = (
            select(func.count()).select_from(VisitModel)
            .where(VisitModel.deleted_at.is_(None), VisitModel.user_id == user_id)
        )

        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if date_from:
            dt = datetime.combine(date_from, datetime.min.time()) if isinstance(date_from, date) else date_from
            query = query.where(VisitModel.date >= dt)
            count_query = count_query.where(VisitModel.date >= dt)
        if date_to:
            dt = datetime.combine(date_to, datetime.max.time()) if isinstance(date_to, date) else date_to
            query = query.where(VisitModel.date <= dt)
            count_query = count_query.where(VisitModel.date <= dt)
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
        query = query.order_by(sort_map.get(sort, VisitModel.date.desc()))

        total = (await self._session.execute(count_query)).scalar() or 0
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, visit: Visit) -> Visit:
        if visit.id:
            model = await self._session.get(VisitModel, visit.id)
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
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        result = await self._session.execute(
            select(VisitModel).where(VisitModel.id == model.id)
            .options(selectinload(VisitModel.position), selectinload(VisitModel.procedure),
                     selectinload(VisitModel.clinic), selectinload(VisitModel.city))
        )
        model = result.scalar_one()
        return self._to_entity(model)

    async def count_by_region(self, user_id: int) -> list[dict]:
        from app.domain.entities import KYIV_TZ
        from datetime import timedelta
        now = datetime.now(KYIV_TZ)
        one_year_ago = now - timedelta(days=365)

        result = await self._session.execute(
            select(
                VisitModel.body_region,
                func.count().label("visit_count"),
                func.count().filter(VisitModel.date >= one_year_ago).label("visits_last_year"),
                func.max(VisitModel.date).label("last_visit_date"),
            )
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None), VisitModel.body_region.isnot(None))
            .group_by(VisitModel.body_region)
        )
        return [dict(row._mapping) for row in result.all()]

    async def list_by_region(self, user_id: int, region: str, limit: int = 20, offset: int = 0) -> list[Visit]:
        result = await self._session.execute(
            select(VisitModel)
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None), VisitModel.body_region == region)
            .options(selectinload(VisitModel.position), selectinload(VisitModel.procedure), selectinload(VisitModel.clinic))
            .order_by(VisitModel.date.desc())
            .offset(offset).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_unmapped(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(VisitModel)
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None), VisitModel.body_region.is_(None))
        )
        return result.scalar() or 0

    async def count_whole_body(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(VisitModel)
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None), VisitModel.body_region == "whole_body")
        )
        return result.scalar() or 0

    async def count_total(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count(VisitModel.id))
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None))
        )
        return result.scalar() or 0

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Visit]:
        result = await self._session.execute(
            select(VisitModel)
            .where(VisitModel.user_id == user_id, VisitModel.deleted_at.is_(None))
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

from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import BiomarkerReference, LabResult, LabTestEntry, KYIV_TZ
from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel


class SqlAlchemyLabResultRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, lab_result_id: int, user_id: int) -> Optional[LabResult]:
        result = await self._session.execute(
            select(LabResultModel)
            .where(
                LabResultModel.id == lab_result_id,
                LabResultModel.user_id == user_id,
                LabResultModel.deleted_at.is_(None),
            )
            .options(selectinload(LabResultModel.entries))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        user_id: int,
        visit_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort: str = "-date",
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[LabResult], int]:
        query = (
            select(LabResultModel)
            .where(LabResultModel.deleted_at.is_(None), LabResultModel.user_id == user_id)
            .options(selectinload(LabResultModel.entries))
        )
        count_query = (
            select(func.count()).select_from(LabResultModel)
            .where(LabResultModel.deleted_at.is_(None), LabResultModel.user_id == user_id)
        )

        if visit_id is not None:
            query = query.where(LabResultModel.visit_id == visit_id)
            count_query = count_query.where(LabResultModel.visit_id == visit_id)
        if date_from:
            dt = datetime.combine(date_from, datetime.min.time()) if isinstance(date_from, date) and not isinstance(date_from, datetime) else date_from
            query = query.where(LabResultModel.date >= dt)
            count_query = count_query.where(LabResultModel.date >= dt)
        if date_to:
            dt = datetime.combine(date_to, datetime.max.time()) if isinstance(date_to, date) and not isinstance(date_to, datetime) else date_to
            query = query.where(LabResultModel.date <= dt)
            count_query = count_query.where(LabResultModel.date <= dt)

        sort_map = {
            "date": LabResultModel.date,
            "-date": LabResultModel.date.desc(),
            "created": LabResultModel.created,
            "-created": LabResultModel.created.desc(),
        }
        query = query.order_by(sort_map.get(sort, LabResultModel.date.desc()))

        total = (await self._session.execute(count_query)).scalar() or 0
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, lab_result: LabResult) -> LabResult:
        if lab_result.id:
            model = await self._session.get(LabResultModel, lab_result.id)
            model.date = lab_result.date
            model.visit_id = lab_result.visit_id
            model.notes = lab_result.notes
            model.deleted_at = lab_result.deleted_at

            # Replace all entries
            for entry_model in list(model.entries):
                await self._session.delete(entry_model)
            await self._session.flush()

            for entry in lab_result.entries:
                entry_model = LabTestEntryModel(
                    lab_result_id=model.id,
                    biomarker_id=entry.biomarker_id,
                    biomarker_name=entry.biomarker_name,
                    value=entry.value,
                    unit=entry.unit,
                    ref_min=entry.ref_min,
                    ref_max=entry.ref_max,
                )
                self._session.add(entry_model)
        else:
            model = LabResultModel(
                user_id=lab_result.user_id,
                visit_id=lab_result.visit_id,
                date=lab_result.date,
                notes=lab_result.notes,
            )
            self._session.add(model)
            await self._session.flush()

            for entry in lab_result.entries:
                entry_model = LabTestEntryModel(
                    lab_result_id=model.id,
                    biomarker_id=entry.biomarker_id,
                    biomarker_name=entry.biomarker_name,
                    value=entry.value,
                    unit=entry.unit,
                    ref_min=entry.ref_min,
                    ref_max=entry.ref_max,
                )
                self._session.add(entry_model)

        await self._session.commit()
        await self._session.refresh(model)
        # Re-fetch with eager loaded entries
        result = await self._session.execute(
            select(LabResultModel)
            .where(LabResultModel.id == model.id)
            .options(selectinload(LabResultModel.entries))
        )
        model = result.scalar_one()
        return self._to_entity(model)

    async def soft_delete(self, lab_result_id: int, user_id: int) -> None:
        now = datetime.now(KYIV_TZ)
        await self._session.execute(
            update(LabResultModel)
            .where(
                LabResultModel.id == lab_result_id,
                LabResultModel.user_id == user_id,
                LabResultModel.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        await self._session.commit()

    async def cascade_soft_delete_by_visit(self, visit_id: int) -> None:
        now = datetime.now(KYIV_TZ)
        await self._session.execute(
            update(LabResultModel)
            .where(
                LabResultModel.visit_id == visit_id,
                LabResultModel.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        await self._session.commit()

    async def biomarker_trend(self, user_id: int, biomarker_name: str) -> list[dict]:
        result = await self._session.execute(
            select(
                LabTestEntryModel.value,
                LabTestEntryModel.unit,
                LabTestEntryModel.ref_min,
                LabTestEntryModel.ref_max,
                LabResultModel.date,
            )
            .join(LabResultModel, LabTestEntryModel.lab_result_id == LabResultModel.id)
            .where(
                LabResultModel.user_id == user_id,
                LabResultModel.deleted_at.is_(None),
                LabTestEntryModel.biomarker_name == biomarker_name,
            )
            .order_by(LabResultModel.date)
        )
        return [
            {
                "date": row.date,
                "value": row.value,
                "unit": row.unit,
                "ref_min": row.ref_min,
                "ref_max": row.ref_max,
            }
            for row in result.all()
        ]

    @staticmethod
    def _to_entity(model: LabResultModel) -> LabResult:
        entries = [
            LabTestEntry(
                id=e.id,
                lab_result_id=e.lab_result_id,
                biomarker_id=e.biomarker_id,
                biomarker_name=e.biomarker_name,
                value=e.value,
                unit=e.unit,
                ref_min=e.ref_min,
                ref_max=e.ref_max,
                created=e.created,
                updated=e.updated,
            )
            for e in (model.entries or [])
        ]
        return LabResult(
            id=model.id,
            user_id=model.user_id,
            visit_id=model.visit_id,
            date=model.date,
            notes=model.notes,
            deleted_at=model.deleted_at,
            created=model.created,
            updated=model.updated,
            entries=entries,
        )

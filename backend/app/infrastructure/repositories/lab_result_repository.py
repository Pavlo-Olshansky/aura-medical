from __future__ import annotations

import builtins
from datetime import date, datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.domain.entities import LabResult, LabTestEntry, KYIV_TZ
from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel
from app.infrastructure.repositories.base_repository import BaseQueryRepository


class SqlAlchemyLabResultRepository(BaseQueryRepository[LabResultModel, LabResult]):
    model_class = LabResultModel

    _load_options = [
        selectinload(LabResultModel.entries),
    ]

    async def get_by_id(self, lab_result_id: int, user_id: int) -> Optional[LabResult]:
        result = await self._session.execute(
            self._base_query()
            .where(LabResultModel.id == lab_result_id, LabResultModel.user_id == user_id)
            .options(*self._load_options)
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
    ) -> tuple[builtins.list[LabResult], int]:
        query = (
            self._base_query()
            .where(LabResultModel.user_id == user_id)
            .options(*self._load_options)
        )
        count_query = (
            self._base_count()
            .where(LabResultModel.user_id == user_id)
        )

        if visit_id is not None:
            query = query.where(LabResultModel.visit_id == visit_id)
            count_query = count_query.where(LabResultModel.visit_id == visit_id)

        query, count_query = self._apply_date_filter(
            query, count_query, LabResultModel.date, date_from, date_to,
        )

        sort_map = {
            "date": LabResultModel.date,
            "-date": LabResultModel.date.desc(),
            "created": LabResultModel.created,
            "-created": LabResultModel.created.desc(),
        }
        query = self._apply_sort(query, sort, sort_map)

        total = (await self._session.execute(count_query)).scalar() or 0
        query = self._apply_pagination(query, page, size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, lab_result: LabResult) -> LabResult:
        if lab_result.id:
            model = await self._session.get(LabResultModel, lab_result.id)
            assert model is not None
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
            .options(*self._load_options)
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

    async def biomarker_trend(self, user_id: int, biomarker_name: str) -> builtins.list[dict]:
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

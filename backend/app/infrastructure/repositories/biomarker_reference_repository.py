from __future__ import annotations
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import BiomarkerReference
from app.infrastructure.models.biomarker_reference import BiomarkerReferenceModel
from app.infrastructure.models.lab_result import LabTestEntryModel


class SqlAlchemyBiomarkerReferenceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, ref_id: int) -> Optional[BiomarkerReference]:
        result = await self._session.execute(
            select(BiomarkerReferenceModel).where(BiomarkerReferenceModel.id == ref_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, search: Optional[str] = None) -> list[BiomarkerReference]:
        query = select(BiomarkerReferenceModel)
        if search:
            query = query.where(BiomarkerReferenceModel.name.ilike(f"%{search}%"))
        query = query.order_by(BiomarkerReferenceModel.sort_order, BiomarkerReferenceModel.name)
        result = await self._session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def save(self, ref: BiomarkerReference) -> BiomarkerReference:
        if ref.id:
            model = await self._session.get(BiomarkerReferenceModel, ref.id)
            assert model is not None
            for attr in ("name", "abbreviation", "unit", "category",
                         "ref_min", "ref_max", "ref_min_male", "ref_max_male",
                         "ref_min_female", "ref_max_female", "sort_order"):
                setattr(model, attr, getattr(ref, attr))
        else:
            model = BiomarkerReferenceModel(
                name=ref.name, abbreviation=ref.abbreviation, unit=ref.unit,
                category=ref.category, ref_min=ref.ref_min, ref_max=ref.ref_max,
                ref_min_male=ref.ref_min_male, ref_max_male=ref.ref_max_male,
                ref_min_female=ref.ref_min_female, ref_max_female=ref.ref_max_female,
                sort_order=ref.sort_order,
            )
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, ref_id: int) -> None:
        from sqlalchemy import delete as sa_delete
        await self._session.execute(
            sa_delete(BiomarkerReferenceModel).where(BiomarkerReferenceModel.id == ref_id)
        )
        await self._session.commit()

    async def reference_count(self, ref_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(LabTestEntryModel)
            .where(LabTestEntryModel.biomarker_id == ref_id)
        )
        return result.scalar() or 0

    async def is_referenced(self, ref_id: int) -> bool:
        return (await self.reference_count(ref_id)) > 0

    @staticmethod
    def _to_entity(model: BiomarkerReferenceModel) -> BiomarkerReference:
        return BiomarkerReference(
            id=model.id, name=model.name, abbreviation=model.abbreviation,
            unit=model.unit, category=model.category,
            ref_min=model.ref_min, ref_max=model.ref_max,
            ref_min_male=model.ref_min_male, ref_max_male=model.ref_max_male,
            ref_min_female=model.ref_min_female, ref_max_female=model.ref_max_female,
            sort_order=model.sort_order,
            created=model.created, updated=model.updated,
        )

from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Vaccination, KYIV_TZ
from app.infrastructure.models.vaccination import VaccinationModel


class SqlAlchemyVaccinationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, vaccination_id: int, user_id: int) -> Optional[Vaccination]:
        result = await self._session.execute(
            select(VaccinationModel).where(
                VaccinationModel.id == vaccination_id,
                VaccinationModel.user_id == user_id,
                VaccinationModel.deleted_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list(
        self,
        user_id: int,
        sort: str = "-date",
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Vaccination], int]:
        query = (
            select(VaccinationModel)
            .where(VaccinationModel.deleted_at.is_(None), VaccinationModel.user_id == user_id)
        )
        count_query = (
            select(func.count()).select_from(VaccinationModel)
            .where(VaccinationModel.deleted_at.is_(None), VaccinationModel.user_id == user_id)
        )

        sort_map = {
            "date": VaccinationModel.date,
            "-date": VaccinationModel.date.desc(),
            "created": VaccinationModel.created,
            "-created": VaccinationModel.created.desc(),
        }
        query = query.order_by(sort_map.get(sort, VaccinationModel.date.desc()))

        total = (await self._session.execute(count_query)).scalar() or 0
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, vaccination: Vaccination) -> Vaccination:
        if vaccination.id:
            model = await self._session.get(VaccinationModel, vaccination.id)
            for attr in ("date", "vaccine_name", "manufacturer", "lot_number",
                         "dose_number", "next_due_date", "notes", "document_path",
                         "deleted_at"):
                setattr(model, attr, getattr(vaccination, attr))
        else:
            model = VaccinationModel(
                user_id=vaccination.user_id,
                date=vaccination.date,
                vaccine_name=vaccination.vaccine_name,
                manufacturer=vaccination.manufacturer,
                lot_number=vaccination.lot_number,
                dose_number=vaccination.dose_number,
                next_due_date=vaccination.next_due_date,
                notes=vaccination.notes,
                document_path=vaccination.document_path,
            )
            self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def list_upcoming(self, user_id: int) -> list[Vaccination]:
        now = datetime.now(KYIV_TZ)
        result = await self._session.execute(
            select(VaccinationModel).where(
                VaccinationModel.user_id == user_id,
                VaccinationModel.deleted_at.is_(None),
                VaccinationModel.next_due_date.isnot(None),
                VaccinationModel.next_due_date > now,
            ).order_by(VaccinationModel.next_due_date)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_overdue(self, user_id: int) -> list[Vaccination]:
        now = datetime.now(KYIV_TZ)
        result = await self._session.execute(
            select(VaccinationModel).where(
                VaccinationModel.user_id == user_id,
                VaccinationModel.deleted_at.is_(None),
                VaccinationModel.next_due_date.isnot(None),
                VaccinationModel.next_due_date <= now,
            ).order_by(VaccinationModel.next_due_date)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: VaccinationModel) -> Vaccination:
        return Vaccination(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            vaccine_name=model.vaccine_name,
            manufacturer=model.manufacturer,
            lot_number=model.lot_number,
            dose_number=model.dose_number,
            next_due_date=model.next_due_date,
            notes=model.notes,
            document_path=model.document_path,
            deleted_at=model.deleted_at,
            created=model.created,
            updated=model.updated,
        )

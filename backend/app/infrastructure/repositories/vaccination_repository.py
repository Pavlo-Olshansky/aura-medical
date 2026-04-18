from __future__ import annotations

import builtins
from typing import Optional

from app.domain.entities import Vaccination
from app.infrastructure.models.vaccination import VaccinationModel
from app.infrastructure.repositories.base_repository import BaseQueryRepository


class SqlAlchemyVaccinationRepository(BaseQueryRepository[VaccinationModel, Vaccination]):
    model_class = VaccinationModel

    async def get_by_id(self, vaccination_id: int, user_id: int) -> Optional[Vaccination]:
        result = await self._session.execute(
            self._base_query().where(
                VaccinationModel.id == vaccination_id,
                VaccinationModel.user_id == user_id,
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
    ) -> tuple[builtins.list[Vaccination], int]:
        query = (
            self._base_query()
            .where(VaccinationModel.user_id == user_id)
        )
        count_query = (
            self._base_count()
            .where(VaccinationModel.user_id == user_id)
        )

        sort_map = {
            "date": VaccinationModel.date,
            "-date": VaccinationModel.date.desc(),
            "created": VaccinationModel.created,
            "-created": VaccinationModel.created.desc(),
        }
        query = self._apply_sort(query, sort, sort_map)

        total = (await self._session.execute(count_query)).scalar() or 0
        query = self._apply_pagination(query, page, size)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models], total

    async def save(self, vaccination: Vaccination) -> Vaccination:
        if vaccination.id:
            model = await self._session.get(VaccinationModel, vaccination.id)
            assert model is not None
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
        model = await self._save_and_refresh(model)
        return self._to_entity(model)

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

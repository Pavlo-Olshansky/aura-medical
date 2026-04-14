from __future__ import annotations
from typing import Optional

from app.application.commands import CreateVaccinationCommand, UpdateVaccinationCommand
from app.application.update_utils import apply_update
from app.domain.entities import Vaccination
from app.domain.exceptions import EntityNotFound
from app.domain.repositories import DocumentStorage
from app.infrastructure.repositories.vaccination_repository import SqlAlchemyVaccinationRepository


class VaccinationAppService:
    def __init__(self, repo: SqlAlchemyVaccinationRepository, storage: DocumentStorage):
        self._repo = repo
        self._storage = storage

    async def get(self, vaccination_id: int, user_id: int) -> Vaccination:
        vaccination = await self._repo.get_by_id(vaccination_id, user_id)
        if not vaccination:
            raise EntityNotFound("Vaccination not found")
        return vaccination

    async def list(self, user_id: int, sort: str = "-date", page: int = 1, size: int = 20) -> tuple[list[Vaccination], int]:
        return await self._repo.list(user_id, sort, page, size)

    async def create(
        self,
        user_id: int,
        cmd: CreateVaccinationCommand,
        file_data: Optional[tuple[str, bytes]] = None,
    ) -> Vaccination:
        vaccination = Vaccination(
            user_id=user_id,
            date=cmd.date,
            vaccine_name=cmd.vaccine_name,
            manufacturer=cmd.manufacturer,
            lot_number=cmd.lot_number,
            dose_number=cmd.dose_number,
            next_due_date=cmd.next_due_date,
            notes=cmd.notes,
        )
        if file_data:
            path = await self._storage.save(file_data[0], file_data[1], vaccination.date, None)
            vaccination.document_path = path
        return await self._repo.save(vaccination)

    async def update(
        self,
        vaccination_id: int,
        user_id: int,
        cmd: UpdateVaccinationCommand,
        file_data: Optional[tuple[str, bytes]] = None,
    ) -> Vaccination:
        vaccination = await self.get(vaccination_id, user_id)
        apply_update(vaccination, cmd)
        if file_data:
            path = await self._storage.save(file_data[0], file_data[1], vaccination.date, None)
            vaccination.document_path = path
        return await self._repo.save(vaccination)

    async def delete(self, vaccination_id: int, user_id: int) -> None:
        vaccination = await self.get(vaccination_id, user_id)
        vaccination.soft_delete()
        await self._repo.save(vaccination)

    async def list_upcoming(self, user_id: int) -> list[Vaccination]:
        return await self._repo.list_upcoming(user_id)

    async def list_overdue(self, user_id: int) -> list[Vaccination]:
        return await self._repo.list_overdue(user_id)

    def get_document_path(self, vaccination: Vaccination) -> Optional[str]:
        if not vaccination.document_path:
            return None
        return self._storage.get_path(vaccination.document_path)

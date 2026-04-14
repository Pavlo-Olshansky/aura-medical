from __future__ import annotations
from typing import Optional

from app.application.commands import CreateVisitCommand, UpdateVisitCommand, VisitFilter
from app.application.update_utils import apply_update
from app.domain.entities import Visit
from app.domain.exceptions import EntityNotFound
from app.domain.repositories import DocumentStorage, VisitRepository


class VisitAppService:
    def __init__(self, repo: VisitRepository, storage: DocumentStorage):
        self._repo = repo
        self._storage = storage

    async def get(self, visit_id: int, user_id: int) -> Visit:
        visit = await self._repo.get_by_id(visit_id, user_id)
        if not visit:
            raise EntityNotFound("Visit not found")
        return visit

    async def list(self, user_id: int, filters: VisitFilter, sort: str, page: int, size: int) -> tuple[list[Visit], int]:
        return await self._repo.list(user_id, filters.to_dict(), sort, page, size)

    async def create(self, user_id: int, cmd: CreateVisitCommand, file_data: Optional[tuple[str, bytes]] = None) -> Visit:
        visit = Visit(
            user_id=user_id, date=cmd.date, position_id=cmd.position_id,
            doctor=cmd.doctor, procedure_id=cmd.procedure_id,
            procedure_details=cmd.procedure_details, clinic_id=cmd.clinic_id,
            city_id=cmd.city_id, link=cmd.link, comment=cmd.comment,
            price=cmd.price,
        )
        if cmd.body_region:
            visit.set_body_region(cmd.body_region)
        if file_data:
            path = await self._storage.save(file_data[0], file_data[1], visit.date, visit.procedure_id)
            visit.attach_document(path)
        return await self._repo.save(visit)

    async def update(self, visit_id: int, user_id: int, cmd: UpdateVisitCommand, file_data: Optional[tuple[str, bytes]] = None) -> Visit:
        visit = await self.get(visit_id, user_id)
        apply_update(visit, cmd, exclude={"body_region"})
        if cmd.body_region is not None:
            visit.set_body_region(cmd.body_region)
        if file_data:
            path = await self._storage.save(file_data[0], file_data[1], visit.date, visit.procedure_id)
            visit.attach_document(path)
        return await self._repo.save(visit)

    async def delete(self, visit_id: int, user_id: int) -> None:
        visit = await self.get(visit_id, user_id)
        visit.soft_delete()
        await self._repo.save(visit)

    def get_document_path(self, visit: Visit) -> Optional[str]:
        if not visit.document:
            return None
        return self._storage.get_path(visit.document)

from __future__ import annotations
from app.domain.entities import Reference
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.domain.repositories import ReferenceRepository


class ReferenceAppService:
    def __init__(self, repo: ReferenceRepository):
        self._repo = repo

    async def list_all(self) -> list[Reference]:
        return await self._repo.list_all()

    async def create(self, name: str) -> Reference:
        ref = Reference(id=None, name=name)
        return await self._repo.save(ref)

    async def update(self, ref_id: int, name: str) -> Reference:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Reference not found")
        ref.name = name
        return await self._repo.save(ref)

    async def delete(self, ref_id: int) -> None:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Reference not found")
        if await self._repo.is_referenced(ref_id):
            raise ReferenceInUse("Cannot delete — referenced by visits")
        # Hard delete for references (they don't use soft delete)
        # For now, we'll need to handle this at the infrastructure level
        raise NotImplementedError("Hard delete not yet implemented in repository")

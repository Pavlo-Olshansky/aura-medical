from __future__ import annotations
from typing import Optional

from app.application.commands import CreateBiomarkerReferenceCommand, UpdateBiomarkerReferenceCommand
from app.domain.entities import BiomarkerReference
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.infrastructure.repositories.biomarker_reference_repository import SqlAlchemyBiomarkerReferenceRepository


class BiomarkerReferenceAppService:
    def __init__(self, repo: SqlAlchemyBiomarkerReferenceRepository):
        self._repo = repo

    async def list_all(self, search: Optional[str] = None) -> list[BiomarkerReference]:
        return await self._repo.list_all(search)

    async def create(self, cmd: CreateBiomarkerReferenceCommand) -> BiomarkerReference:
        ref = BiomarkerReference(
            name=cmd.name, abbreviation=cmd.abbreviation, unit=cmd.unit,
            category=cmd.category, ref_min=cmd.ref_min, ref_max=cmd.ref_max,
            ref_min_male=cmd.ref_min_male, ref_max_male=cmd.ref_max_male,
            ref_min_female=cmd.ref_min_female, ref_max_female=cmd.ref_max_female,
            sort_order=cmd.sort_order,
        )
        return await self._repo.save(ref)

    async def update(self, ref_id: int, cmd: UpdateBiomarkerReferenceCommand) -> BiomarkerReference:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Biomarker reference not found")
        if cmd.name is not None: ref.name = cmd.name
        if cmd.abbreviation is not None: ref.abbreviation = cmd.abbreviation
        if cmd.unit is not None: ref.unit = cmd.unit
        if cmd.category is not None: ref.category = cmd.category
        if cmd.ref_min is not None: ref.ref_min = cmd.ref_min
        if cmd.ref_max is not None: ref.ref_max = cmd.ref_max
        if cmd.ref_min_male is not None: ref.ref_min_male = cmd.ref_min_male
        if cmd.ref_max_male is not None: ref.ref_max_male = cmd.ref_max_male
        if cmd.ref_min_female is not None: ref.ref_min_female = cmd.ref_min_female
        if cmd.ref_max_female is not None: ref.ref_max_female = cmd.ref_max_female
        if cmd.sort_order is not None: ref.sort_order = cmd.sort_order
        return await self._repo.save(ref)

    async def delete(self, ref_id: int) -> None:
        ref = await self._repo.get_by_id(ref_id)
        if not ref:
            raise EntityNotFound("Biomarker reference not found")
        if await self._repo.is_referenced(ref_id):
            raise ReferenceInUse("Cannot delete — referenced by lab test entries")
        await self._repo.delete(ref_id)

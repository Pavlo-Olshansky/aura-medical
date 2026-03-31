from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    get_city_service, get_clinic_service, get_current_user,
    get_position_service, get_procedure_service,
)
from app.application.reference_service import ReferenceAppService
from app.domain.entities import Reference, User
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate


def _to_response(ref: Reference) -> ReferenceResponse:
    return ReferenceResponse(id=ref.id, name=ref.name, created=ref.created, updated=ref.updated)


def _create_reference_router(get_service) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=List[ReferenceResponse])
    async def list_items(
        search: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        service: ReferenceAppService = Depends(get_service),
    ):
        items = await service.list_all()
        if search:
            items = [r for r in items if search.lower() in r.name.lower()]
        return [_to_response(r) for r in items]

    @router.post("/", response_model=ReferenceResponse, status_code=201)
    async def create_item(
        data: ReferenceCreate,
        current_user: User = Depends(get_current_user),
        service: ReferenceAppService = Depends(get_service),
    ):
        try:
            return _to_response(await service.create(data.name))
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exists")

    @router.put("/{item_id}", response_model=ReferenceResponse)
    async def update_item(
        item_id: int,
        data: ReferenceUpdate,
        current_user: User = Depends(get_current_user),
        service: ReferenceAppService = Depends(get_service),
    ):
        try:
            return _to_response(await service.update(item_id, data.name))
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exists")

    @router.delete("/{item_id}", status_code=204)
    async def delete_item(
        item_id: int,
        current_user: User = Depends(get_current_user),
        service: ReferenceAppService = Depends(get_service),
    ):
        ref = await service._repo.get_by_id(item_id)
        if not ref:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        ref_count = await service._repo.reference_count(item_id)
        if ref_count > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot delete: referenced by {ref_count} visit(s)")
        # Hard delete at infrastructure level
        from sqlalchemy import delete as sa_delete
        model_class = service._repo._model_class
        session = service._repo._session
        await session.execute(sa_delete(model_class).where(model_class.id == item_id))
        await session.commit()

    return router


positions_router = _create_reference_router(get_position_service)
procedures_router = _create_reference_router(get_procedure_service)
clinics_router = _create_reference_router(get_clinic_service)
cities_router = _create_reference_router(get_city_service)

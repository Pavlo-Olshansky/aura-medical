from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_biomarker_reference_service, get_current_user
from app.application.biomarker_reference_service import BiomarkerReferenceAppService
from app.application.commands import CreateBiomarkerReferenceCommand, UpdateBiomarkerReferenceCommand
from app.domain.entities import BiomarkerReference, User
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.schemas.biomarker_reference import (
    BiomarkerReferenceCreate, BiomarkerReferenceResponse, BiomarkerReferenceUpdate,
)

router = APIRouter()


def _to_response(ref: BiomarkerReference) -> BiomarkerReferenceResponse:
    return BiomarkerReferenceResponse(
        id=ref.id, name=ref.name, abbreviation=ref.abbreviation,
        unit=ref.unit, category=ref.category,
        ref_min=ref.ref_min, ref_max=ref.ref_max,
        ref_min_male=ref.ref_min_male, ref_max_male=ref.ref_max_male,
        ref_min_female=ref.ref_min_female, ref_max_female=ref.ref_max_female,
        sort_order=ref.sort_order, created=ref.created, updated=ref.updated,
    )


@router.get("/", response_model=List[BiomarkerReferenceResponse])
async def list_biomarker_references(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    items = await service.list_all(search)
    return [_to_response(r) for r in items]


@router.post("/", response_model=BiomarkerReferenceResponse, status_code=201)
async def create_biomarker_reference(
    data: BiomarkerReferenceCreate,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    cmd = CreateBiomarkerReferenceCommand(
        name=data.name, abbreviation=data.abbreviation, unit=data.unit,
        category=data.category, ref_min=data.ref_min, ref_max=data.ref_max,
        ref_min_male=data.ref_min_male, ref_max_male=data.ref_max_male,
        ref_min_female=data.ref_min_female, ref_max_female=data.ref_max_female,
    )
    return _to_response(await service.create(cmd))


@router.put("/{ref_id}", response_model=BiomarkerReferenceResponse)
async def update_biomarker_reference(
    ref_id: int,
    data: BiomarkerReferenceUpdate,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    cmd = UpdateBiomarkerReferenceCommand(**data.model_dump(exclude_unset=True))
    try:
        return _to_response(await service.update(ref_id, cmd))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Biomarker reference not found")


@router.delete("/{ref_id}", status_code=204)
async def delete_biomarker_reference(
    ref_id: int,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    try:
        await service.delete(ref_id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Biomarker reference not found")
    except ReferenceInUse as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

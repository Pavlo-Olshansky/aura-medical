from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_biomarker_reference_service, get_current_user
from app.application.biomarker_reference_service import BiomarkerReferenceAppService
from app.application.commands import CreateBiomarkerReferenceCommand, UpdateBiomarkerReferenceCommand
from app.domain.entities import User
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.schemas.biomarker_reference import (
    BiomarkerReferenceCreate, BiomarkerReferenceResponse, BiomarkerReferenceUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[BiomarkerReferenceResponse])
async def list_biomarker_references(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    items = await service.list_all(search)
    return [BiomarkerReferenceResponse.model_validate(r) for r in items]


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
    return BiomarkerReferenceResponse.model_validate(await service.create(cmd))


@router.put("/{ref_id}", response_model=BiomarkerReferenceResponse)
async def update_biomarker_reference(
    ref_id: int,
    data: BiomarkerReferenceUpdate,
    current_user: User = Depends(get_current_user),
    service: BiomarkerReferenceAppService = Depends(get_biomarker_reference_service),
):
    cmd = UpdateBiomarkerReferenceCommand(**data.model_dump(exclude_unset=True))
    try:
        return BiomarkerReferenceResponse.model_validate(await service.update(ref_id, cmd))
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

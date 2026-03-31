import math
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_treatment_service
from app.application.commands import CreateTreatmentCommand, UpdateTreatmentCommand
from app.application.treatment_service import TreatmentAppService
from app.domain.entities import Treatment, User
from app.schemas.treatment import TreatmentCreate, TreatmentListResponse, TreatmentResponse, TreatmentUpdate

router = APIRouter()


def _to_response(t: Treatment) -> TreatmentResponse:
    return TreatmentResponse(
        id=t.id, date_start=t.date_start, name=t.name, days=t.days,
        receipt=t.receipt, status=t.status, body_region=t.body_region,
        created=t.created, updated=t.updated,
    )


@router.get("/", response_model=TreatmentListResponse)
async def list_treatments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    sort: str = Query("-date_start"),
    current_user: User = Depends(get_current_user),
    service: TreatmentAppService = Depends(get_treatment_service),
):
    items, total = await service.list(current_user.id, status_filter, sort, page, size)
    pages = math.ceil(total / size) if total > 0 else 1
    return TreatmentListResponse(items=[_to_response(t) for t in items], total=total, page=page, size=size, pages=pages)


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    service: TreatmentAppService = Depends(get_treatment_service),
):
    return _to_response(await service.get(treatment_id, current_user.id))


@router.post("/", response_model=TreatmentResponse, status_code=201)
async def create_treatment(
    data: TreatmentCreate,
    current_user: User = Depends(get_current_user),
    service: TreatmentAppService = Depends(get_treatment_service),
):
    cmd = CreateTreatmentCommand(
        date_start=data.date_start, name=data.name, days=data.days,
        receipt=data.receipt, body_region=data.body_region,
    )
    return _to_response(await service.create(current_user.id, cmd))


@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_id: int,
    data: TreatmentUpdate,
    current_user: User = Depends(get_current_user),
    service: TreatmentAppService = Depends(get_treatment_service),
):
    cmd = UpdateTreatmentCommand(**data.model_dump(exclude_unset=True))
    return _to_response(await service.update(treatment_id, current_user.id, cmd))


@router.delete("/{treatment_id}", status_code=204)
async def delete_treatment(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    service: TreatmentAppService = Depends(get_treatment_service),
):
    await service.delete(treatment_id, current_user.id)

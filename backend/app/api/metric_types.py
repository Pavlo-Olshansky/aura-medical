from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_metric_type_service
from app.application.commands import CreateMetricTypeCommand, UpdateMetricTypeCommand
from app.application.metric_type_service import MetricTypeAppService
from app.domain.entities import User
from app.domain.exceptions import EntityNotFound, ReferenceInUse
from app.schemas.metric_type import MetricTypeCreate, MetricTypeResponse, MetricTypeUpdate

router = APIRouter()


@router.get("/", response_model=List[MetricTypeResponse])
async def list_metric_types(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: MetricTypeAppService = Depends(get_metric_type_service),
):
    items = await service.list_all(search)
    return [MetricTypeResponse.model_validate(r) for r in items]


@router.post("/", response_model=MetricTypeResponse, status_code=201)
async def create_metric_type(
    data: MetricTypeCreate,
    current_user: User = Depends(get_current_user),
    service: MetricTypeAppService = Depends(get_metric_type_service),
):
    cmd = CreateMetricTypeCommand(
        name=data.name, unit=data.unit,
        has_secondary_value=data.has_secondary_value,
        ref_min=data.ref_min, ref_max=data.ref_max,
        ref_min_secondary=data.ref_min_secondary,
        ref_max_secondary=data.ref_max_secondary,
    )
    return MetricTypeResponse.model_validate(await service.create(cmd))


@router.put("/{ref_id}", response_model=MetricTypeResponse)
async def update_metric_type(
    ref_id: int,
    data: MetricTypeUpdate,
    current_user: User = Depends(get_current_user),
    service: MetricTypeAppService = Depends(get_metric_type_service),
):
    cmd = UpdateMetricTypeCommand(**data.model_dump(exclude_unset=True))
    try:
        return MetricTypeResponse.model_validate(await service.update(ref_id, cmd))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric type not found")


@router.delete("/{ref_id}", status_code=204)
async def delete_metric_type(
    ref_id: int,
    current_user: User = Depends(get_current_user),
    service: MetricTypeAppService = Depends(get_metric_type_service),
):
    try:
        await service.delete(ref_id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric type not found")
    except ReferenceInUse as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

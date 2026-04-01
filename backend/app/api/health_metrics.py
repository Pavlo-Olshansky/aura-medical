import math
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_health_metric_service
from app.application.commands import CreateHealthMetricCommand, UpdateHealthMetricCommand
from app.application.health_metric_service import HealthMetricAppService
from app.domain.entities import HealthMetric, User
from app.domain.exceptions import DomainError, EntityNotFound
from app.schemas.health_metric import (
    HealthMetricCreate, HealthMetricListResponse, HealthMetricResponse, HealthMetricUpdate,
    MetricTrendPoint, MetricTrendResponse,
)
from app.schemas.metric_type import MetricTypeResponse

router = APIRouter()


def _to_response(m: HealthMetric) -> HealthMetricResponse:
    mt = None
    if m.metric_type:
        mt = MetricTypeResponse(
            id=m.metric_type.id, name=m.metric_type.name, unit=m.metric_type.unit,
            has_secondary_value=m.metric_type.has_secondary_value,
            ref_min=m.metric_type.ref_min, ref_max=m.metric_type.ref_max,
            ref_min_secondary=m.metric_type.ref_min_secondary,
            ref_max_secondary=m.metric_type.ref_max_secondary,
            sort_order=m.metric_type.sort_order,
            created=m.metric_type.created, updated=m.metric_type.updated,
        )
    return HealthMetricResponse(
        id=m.id, metric_type_id=m.metric_type_id, metric_type=mt,
        date=m.date, value=m.value, secondary_value=m.secondary_value,
        notes=m.notes, created=m.created, updated=m.updated,
    )


@router.get("/trend", response_model=MetricTrendResponse)
async def metric_trend(
    metric_type_id: int = Query(...),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    points = await service.trend(current_user.id, metric_type_id, date_from, date_to)
    # Fetch metric type info for response
    mt = await service._metric_type_repo.get_by_id(metric_type_id)
    if not mt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric type not found")
    return MetricTrendResponse(
        metric_type=mt.name, unit=mt.unit,
        ref_min=mt.ref_min, ref_max=mt.ref_max,
        ref_min_secondary=mt.ref_min_secondary,
        ref_max_secondary=mt.ref_max_secondary,
        data_points=[
            MetricTrendPoint(
                date=p["date"], value=p["value"],
                secondary_value=p.get("secondary_value"),
            )
            for p in points
        ],
    )


@router.get("/", response_model=HealthMetricListResponse)
async def list_health_metrics(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    metric_type_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: str = Query("-date"),
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    items, total = await service.list(current_user.id, metric_type_id, date_from, date_to, sort, page, size)
    pages = math.ceil(total / size) if total > 0 else 1
    return HealthMetricListResponse(
        items=[_to_response(m) for m in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.get("/{metric_id}", response_model=HealthMetricResponse)
async def get_health_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    try:
        return _to_response(await service.get(metric_id, current_user.id))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health metric not found")


@router.post("/", response_model=HealthMetricResponse, status_code=201)
async def create_health_metric(
    data: HealthMetricCreate,
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    cmd = CreateHealthMetricCommand(
        metric_type_id=data.metric_type_id, date=data.date,
        value=data.value, secondary_value=data.secondary_value, notes=data.notes,
    )
    try:
        return _to_response(await service.create(current_user.id, cmd))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric type not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put("/{metric_id}", response_model=HealthMetricResponse)
async def update_health_metric(
    metric_id: int,
    data: HealthMetricUpdate,
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    cmd = UpdateHealthMetricCommand(**data.model_dump(exclude_unset=True))
    try:
        return _to_response(await service.update(metric_id, current_user.id, cmd))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health metric not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete("/{metric_id}", status_code=204)
async def delete_health_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user),
    service: HealthMetricAppService = Depends(get_health_metric_service),
):
    try:
        await service.delete(metric_id, current_user.id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health metric not found")

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user, get_lab_result_service
from app.application.commands import CreateLabResultCommand, LabTestEntryData, UpdateLabResultCommand
from app.application.lab_result_service import LabResultAppService
from app.application.pagination import calculate_pages
from app.domain.entities import LabResult, User
from app.domain.exceptions import EntityNotFound
from app.schemas.lab_result import (
    BiomarkerTrendPoint, BiomarkerTrendResponse,
    LabResultCreate, LabResultListItem,
    LabResultResponse, LabResultUpdate,
)
from app.schemas.pagination import PaginatedResponse

router = APIRouter()


def _to_list_item(lr: LabResult) -> LabResultListItem:
    entries_count = len(lr.entries) if lr.entries else 0
    out_of_range_count = sum(1 for e in (lr.entries or []) if e.is_normal is False)
    assert lr.id is not None
    assert lr.created is not None
    assert lr.updated is not None
    return LabResultListItem(
        id=lr.id, visit_id=lr.visit_id, date=lr.date, notes=lr.notes,
        entries_count=entries_count, out_of_range_count=out_of_range_count,
        created=lr.created, updated=lr.updated,
    )


@router.get("/biomarker-trend", response_model=BiomarkerTrendResponse)
async def biomarker_trend(
    biomarker_name: str = Query(...),
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    points = await service.biomarker_trend(current_user.id, biomarker_name)
    return BiomarkerTrendResponse(
        biomarker_name=biomarker_name,
        data_points=[
            BiomarkerTrendPoint(
                date=p["date"], value=p["value"],
                ref_min=p.get("ref_min"), ref_max=p.get("ref_max"),
            )
            for p in points
        ],
    )


@router.get("/", response_model=PaginatedResponse[LabResultListItem])
async def list_lab_results(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    visit_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: str = Query("-date"),
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    items, total = await service.list(current_user.id, visit_id, date_from, date_to, sort, page, size)
    pages = calculate_pages(total, size)
    return PaginatedResponse[LabResultListItem](
        items=[_to_list_item(lr) for lr in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.get("/{lab_result_id}", response_model=LabResultResponse)
async def get_lab_result(
    lab_result_id: int,
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    try:
        return LabResultResponse.model_validate(await service.get(lab_result_id, current_user.id))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found")


@router.post("/", response_model=LabResultResponse, status_code=201)
async def create_lab_result(
    data: LabResultCreate,
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    cmd = CreateLabResultCommand(
        date=data.date, visit_id=data.visit_id, notes=data.notes,
        entries=[
            LabTestEntryData(
                biomarker_id=e.biomarker_id, biomarker_name=e.biomarker_name,
                value=e.value, unit=e.unit, ref_min=e.ref_min, ref_max=e.ref_max,
            )
            for e in data.entries
        ],
    )
    return LabResultResponse.model_validate(await service.create(current_user.id, cmd))


@router.put("/{lab_result_id}", response_model=LabResultResponse)
async def update_lab_result(
    lab_result_id: int,
    data: LabResultUpdate,
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    entries = None
    if data.entries is not None:
        entries = [
            LabTestEntryData(
                biomarker_id=e.biomarker_id, biomarker_name=e.biomarker_name,
                value=e.value, unit=e.unit, ref_min=e.ref_min, ref_max=e.ref_max,
            )
            for e in data.entries
        ]
    cmd = UpdateLabResultCommand(
        date=data.date, visit_id=data.visit_id, notes=data.notes,
        entries=entries,
    )
    try:
        return LabResultResponse.model_validate(await service.update(lab_result_id, current_user.id, cmd))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found")


@router.delete("/{lab_result_id}", status_code=204)
async def delete_lab_result(
    lab_result_id: int,
    current_user: User = Depends(get_current_user),
    service: LabResultAppService = Depends(get_lab_result_service),
):
    try:
        await service.delete(lab_result_id, current_user.id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab result not found")

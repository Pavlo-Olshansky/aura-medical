import math
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user, get_vaccination_service
from app.application.commands import CreateVaccinationCommand, UpdateVaccinationCommand
from app.application.vaccination_service import VaccinationAppService
from app.domain.entities import User, Vaccination
from app.domain.exceptions import EntityNotFound
from app.schemas.vaccination import VaccinationListResponse, VaccinationResponse

router = APIRouter()


def _to_response(v: Vaccination) -> VaccinationResponse:
    return VaccinationResponse(
        id=v.id, date=v.date, vaccine_name=v.vaccine_name,
        manufacturer=v.manufacturer, lot_number=v.lot_number,
        dose_number=v.dose_number, next_due_date=v.next_due_date,
        notes=v.notes, has_document=v.has_document, status=v.status,
        created=v.created, updated=v.updated,
    )


@router.get("/", response_model=VaccinationListResponse)
async def list_vaccinations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str = Query("-date"),
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    items, total = await service.list(current_user.id, sort, page, size)
    pages = math.ceil(total / size) if total > 0 else 1
    return VaccinationListResponse(
        items=[_to_response(v) for v in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.get("/{vaccination_id}", response_model=VaccinationResponse)
async def get_vaccination(
    vaccination_id: int,
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    try:
        return _to_response(await service.get(vaccination_id, current_user.id))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccination not found")


@router.post("/", response_model=VaccinationResponse, status_code=201)
async def create_vaccination(
    date: datetime = Form(...),
    vaccine_name: str = Form(...),
    manufacturer: Optional[str] = Form(None),
    lot_number: Optional[str] = Form(None),
    dose_number: int = Form(1),
    next_due_date: Optional[datetime] = Form(None),
    notes: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    cmd = CreateVaccinationCommand(
        date=date, vaccine_name=vaccine_name, manufacturer=manufacturer,
        lot_number=lot_number, dose_number=dose_number,
        next_due_date=next_due_date, notes=notes,
    )
    file_data = None
    if document and document.filename:
        file_data = (document.filename, await document.read())
    return _to_response(await service.create(current_user.id, cmd, file_data))


@router.put("/{vaccination_id}", response_model=VaccinationResponse)
async def update_vaccination(
    vaccination_id: int,
    date: Optional[datetime] = Form(None),
    vaccine_name: Optional[str] = Form(None),
    manufacturer: Optional[str] = Form(None),
    lot_number: Optional[str] = Form(None),
    dose_number: Optional[int] = Form(None),
    next_due_date: Optional[datetime] = Form(None),
    notes: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    cmd = UpdateVaccinationCommand(
        date=date, vaccine_name=vaccine_name, manufacturer=manufacturer,
        lot_number=lot_number, dose_number=dose_number,
        next_due_date=next_due_date, notes=notes,
    )
    file_data = None
    if document and document.filename:
        file_data = (document.filename, await document.read())
    try:
        return _to_response(await service.update(vaccination_id, current_user.id, cmd, file_data))
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccination not found")


@router.delete("/{vaccination_id}", status_code=204)
async def delete_vaccination(
    vaccination_id: int,
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    try:
        await service.delete(vaccination_id, current_user.id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccination not found")


@router.get("/{vaccination_id}/document")
async def get_vaccination_document(
    vaccination_id: int,
    current_user: User = Depends(get_current_user),
    service: VaccinationAppService = Depends(get_vaccination_service),
):
    try:
        vaccination = await service.get(vaccination_id, current_user.id)
    except EntityNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccination not found")
    path = service.get_document_path(vaccination)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No document attached")
    return FileResponse(path)

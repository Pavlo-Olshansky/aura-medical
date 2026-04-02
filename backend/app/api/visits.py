import os
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user, get_visit_service
from app.application.commands import CreateVisitCommand, UpdateVisitCommand, VisitFilter
from app.application.pagination import calculate_pages
from app.application.visit_service import VisitAppService
from app.domain.entities import User
from app.schemas.visit import VisitListResponse, VisitResponse

router = APIRouter()


@router.get("/", response_model=VisitListResponse)
async def list_visits(
    page: int = 1, size: int = 20,
    date_from: Optional[date] = None, date_to: Optional[date] = None,
    clinic_id: Optional[int] = None, city_id: Optional[int] = None,
    procedure_id: Optional[int] = None, position_id: Optional[int] = None,
    body_region: Optional[str] = None, sort: str = "-date",
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    filters = VisitFilter(date_from=date_from, date_to=date_to, clinic_id=clinic_id,
                          city_id=city_id, procedure_id=procedure_id, position_id=position_id,
                          body_region=body_region)
    items, total = await service.list(current_user.id, filters, sort, page, size)
    pages = calculate_pages(total, size)
    return VisitListResponse(items=[VisitResponse.model_validate(v) for v in items], total=total, page=page, size=size, pages=pages)


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    return VisitResponse.model_validate(await service.get(visit_id, current_user.id))


@router.post("/", response_model=VisitResponse, status_code=201)
async def create_visit(
    date: datetime = Form(...),
    position_id: Optional[int] = Form(None), doctor: Optional[str] = Form(None),
    procedure_id: Optional[int] = Form(None), procedure_details: Optional[str] = Form(None),
    clinic_id: Optional[int] = Form(None), city_id: Optional[int] = Form(None),
    link: Optional[str] = Form(None), comment: Optional[str] = Form(None),
    body_region: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    cmd = CreateVisitCommand(date=date, position_id=position_id, doctor=doctor,
                             procedure_id=procedure_id, procedure_details=procedure_details,
                             clinic_id=clinic_id, city_id=city_id, link=link,
                             comment=comment, body_region=body_region,
                             price=Decimal(str(price)) if price is not None else None)
    file_data = None
    if document and document.filename:
        file_data = (document.filename, await document.read())
    return VisitResponse.model_validate(await service.create(current_user.id, cmd, file_data))


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    date: Optional[datetime] = Form(None),
    position_id: Optional[int] = Form(None), doctor: Optional[str] = Form(None),
    procedure_id: Optional[int] = Form(None), procedure_details: Optional[str] = Form(None),
    clinic_id: Optional[int] = Form(None), city_id: Optional[int] = Form(None),
    link: Optional[str] = Form(None), comment: Optional[str] = Form(None),
    body_region: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    cmd = UpdateVisitCommand(date=date, position_id=position_id, doctor=doctor,
                             procedure_id=procedure_id, procedure_details=procedure_details,
                             clinic_id=clinic_id, city_id=city_id, link=link,
                             comment=comment, body_region=body_region,
                             price=Decimal(str(price)) if price is not None else None)
    file_data = None
    if document and document.filename:
        file_data = (document.filename, await document.read())
    return VisitResponse.model_validate(await service.update(visit_id, current_user.id, cmd, file_data))


@router.delete("/{visit_id}", status_code=204)
async def delete_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    await service.delete(visit_id, current_user.id)


@router.get("/{visit_id}/document")
async def get_visit_document(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    service: VisitAppService = Depends(get_visit_service),
):
    visit = await service.get(visit_id, current_user.id)
    path = service.get_document_path(visit)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No document attached")
    return FileResponse(path)

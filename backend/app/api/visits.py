import math
import os
import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_session
from app.models.reference import Procedure
from app.models.user import User
from app.models.visit import Visit
from app.schemas.visit import VisitListResponse, VisitResponse

router = APIRouter()

SORT_FIELDS = {
    "date": Visit.date,
    "-date": Visit.date.desc(),
    "created": Visit.created,
    "-created": Visit.created.desc(),
}


def _build_visit_response(visit: Visit) -> VisitResponse:
    return VisitResponse.model_validate(
        visit,
        from_attributes=True,
        context={"has_document": bool(visit.document)},
    )


def _visit_to_dict(visit: Visit) -> dict:
    data = {
        "id": visit.id,
        "date": visit.date,
        "position": visit.position,
        "doctor": visit.doctor,
        "procedure": visit.procedure,
        "procedure_details": visit.procedure_details,
        "clinic": visit.clinic,
        "city": visit.city,
        "document": visit.document,
        "has_document": bool(visit.document),
        "body_region": visit.body_region,
        "link": visit.link,
        "comment": visit.comment,
        "created": visit.created,
        "updated": visit.updated,
    }
    return data


async def _save_document(
    file: UploadFile,
    visit_date: datetime,
    procedure_id: Optional[int],
    session: AsyncSession,
) -> str:
    year = visit_date.year

    if procedure_id:
        result = await session.execute(
            select(Procedure).where(Procedure.id == procedure_id)
        )
        procedure = result.scalar_one_or_none()
        procedure_name = procedure.name if procedure else "інше"
    else:
        procedure_name = "інше"

    subdir = f"{year}_{procedure_name}"
    docs_dir = os.path.join(settings.DOCUMENTS_DIR, subdir)
    os.makedirs(docs_dir, exist_ok=True)

    original_filename = file.filename or "document"
    filepath = os.path.join(docs_dir, original_filename)

    if os.path.exists(filepath):
        name, ext = os.path.splitext(original_filename)
        unique_suffix = uuid.uuid4().hex[:8]
        original_filename = f"{name}_{unique_suffix}{ext}"
        filepath = os.path.join(docs_dir, original_filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    relative_path = os.path.join("documents", subdir, original_filename)
    return relative_path


@router.get("/", response_model=VisitListResponse)
async def list_visits(
    page: int = 1,
    size: int = 20,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    clinic_id: Optional[int] = None,
    city_id: Optional[int] = None,
    procedure_id: Optional[int] = None,
    position_id: Optional[int] = None,
    body_region: Optional[str] = None,
    sort: str = "-date",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VisitListResponse:
    query = (
        select(Visit)
        .where(Visit.deleted_at.is_(None))
        .where(Visit.user_id == current_user.id)
        .options(
            selectinload(Visit.position),
            selectinload(Visit.procedure),
            selectinload(Visit.clinic),
            selectinload(Visit.city),
        )
    )

    count_query = (
        select(func.count())
        .select_from(Visit)
        .where(Visit.deleted_at.is_(None))
        .where(Visit.user_id == current_user.id)
    )

    if date_from:
        query = query.where(Visit.date >= datetime.combine(date_from, datetime.min.time()))
        count_query = count_query.where(Visit.date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Visit.date <= datetime.combine(date_to, datetime.max.time()))
        count_query = count_query.where(Visit.date <= datetime.combine(date_to, datetime.max.time()))
    if clinic_id:
        query = query.where(Visit.clinic_id == clinic_id)
        count_query = count_query.where(Visit.clinic_id == clinic_id)
    if city_id:
        query = query.where(Visit.city_id == city_id)
        count_query = count_query.where(Visit.city_id == city_id)
    if procedure_id:
        query = query.where(Visit.procedure_id == procedure_id)
        count_query = count_query.where(Visit.procedure_id == procedure_id)
    if position_id:
        query = query.where(Visit.position_id == position_id)
        count_query = count_query.where(Visit.position_id == position_id)
    if body_region:
        query = query.where(Visit.body_region == body_region)
        count_query = count_query.where(Visit.body_region == body_region)

    order = SORT_FIELDS.get(sort, Visit.date.desc())
    query = query.order_by(order)

    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0
    pages = math.ceil(total / size) if size > 0 else 0

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await session.execute(query)
    visits = result.scalars().all()

    items = [VisitResponse(**_visit_to_dict(v)) for v in visits]

    return VisitListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VisitResponse:
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit_id, Visit.deleted_at.is_(None), Visit.user_id == current_user.id)
        .options(
            selectinload(Visit.position),
            selectinload(Visit.procedure),
            selectinload(Visit.clinic),
            selectinload(Visit.city),
        )
    )
    visit = result.scalar_one_or_none()
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    return VisitResponse(**_visit_to_dict(visit))


@router.post("/", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    date: datetime = Form(...),
    position_id: Optional[int] = Form(None),
    doctor: Optional[str] = Form(None),
    procedure_id: Optional[int] = Form(None),
    procedure_details: Optional[str] = Form(None),
    clinic_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    link: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
    body_region: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VisitResponse:
    visit = Visit(
        user_id=current_user.id,
        date=date,
        position_id=position_id,
        doctor=doctor,
        procedure_id=procedure_id,
        procedure_details=procedure_details,
        clinic_id=clinic_id,
        city_id=city_id,
        link=link,
        comment=comment,
        body_region=body_region,
    )

    if document and document.filename:
        visit.document = await _save_document(document, date, procedure_id, session)

    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    # Eagerly load relationships for response
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit.id)
        .options(
            selectinload(Visit.position),
            selectinload(Visit.procedure),
            selectinload(Visit.clinic),
            selectinload(Visit.city),
        )
    )
    visit = result.scalar_one()

    return VisitResponse(**_visit_to_dict(visit))


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    date: Optional[datetime] = Form(None),
    position_id: Optional[int] = Form(None),
    doctor: Optional[str] = Form(None),
    procedure_id: Optional[int] = Form(None),
    procedure_details: Optional[str] = Form(None),
    clinic_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    link: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
    body_region: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VisitResponse:
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit_id, Visit.deleted_at.is_(None), Visit.user_id == current_user.id)
    )
    visit = result.scalar_one_or_none()
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    if date is not None:
        visit.date = date
    if position_id is not None:
        visit.position_id = position_id
    if doctor is not None:
        visit.doctor = doctor
    if procedure_id is not None:
        visit.procedure_id = procedure_id
    if procedure_details is not None:
        visit.procedure_details = procedure_details
    if clinic_id is not None:
        visit.clinic_id = clinic_id
    if city_id is not None:
        visit.city_id = city_id
    if link is not None:
        visit.link = link
    if comment is not None:
        visit.comment = comment
    if body_region is not None:
        visit.body_region = body_region

    if document and document.filename:
        effective_date = date if date is not None else visit.date
        effective_procedure_id = procedure_id if procedure_id is not None else visit.procedure_id
        visit.document = await _save_document(document, effective_date, effective_procedure_id, session)

    await session.commit()
    await session.refresh(visit)

    # Eagerly load relationships for response
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit.id)
        .options(
            selectinload(Visit.position),
            selectinload(Visit.procedure),
            selectinload(Visit.clinic),
            selectinload(Visit.city),
        )
    )
    visit = result.scalar_one()

    return VisitResponse(**_visit_to_dict(visit))


@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit_id, Visit.deleted_at.is_(None), Visit.user_id == current_user.id)
    )
    visit = result.scalar_one_or_none()
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    visit.deleted_at = datetime.utcnow()
    await session.commit()


@router.get("/{visit_id}/document")
async def get_visit_document(
    visit_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    result = await session.execute(
        select(Visit)
        .where(Visit.id == visit_id, Visit.deleted_at.is_(None), Visit.user_id == current_user.id)
    )
    visit = result.scalar_one_or_none()
    if visit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visit not found")

    if not visit.document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No document attached")

    # document is stored as "documents/subdir/filename", resolve relative to DOCUMENTS_DIR parent
    docs_parent = os.path.dirname(settings.DOCUMENTS_DIR)
    file_path = os.path.join(docs_parent, visit.document)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No document attached")

    return FileResponse(file_path)

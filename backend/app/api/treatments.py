import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models.treatment import Treatment
from app.models.user import User
from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentListResponse,
    TreatmentResponse,
    TreatmentUpdate,
)
from app.services.treatment import compute_status

router = APIRouter()


def _treatment_to_response(treatment: Treatment) -> TreatmentResponse:
    return TreatmentResponse(
        id=treatment.id,
        date_start=treatment.date_start,
        name=treatment.name,
        days=treatment.days,
        receipt=treatment.receipt,
        status=compute_status(treatment.date_start, treatment.days),
        body_region=treatment.body_region,
        created=treatment.created,
        updated=treatment.updated,
    )


@router.get("/", response_model=TreatmentListResponse)
async def list_treatments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    sort: str = Query("-date_start"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    base_filter = (
        Treatment.user_id == current_user.id,
        Treatment.deleted_at.is_(None),
    )

    # Count total (before status filtering, we need to apply status filter in-memory)
    # First, get all matching records to filter by computed status
    query = select(Treatment).where(*base_filter)

    # Apply sort
    desc = sort.startswith("-")
    sort_field = sort.lstrip("-")
    column = getattr(Treatment, sort_field, Treatment.date_start)
    if desc:
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    result = await session.execute(query)
    all_treatments = list(result.scalars().all())

    # Apply status filter in-memory (status is computed, not stored)
    if status_filter in ("active", "completed"):
        all_treatments = [
            t for t in all_treatments
            if compute_status(t.date_start, t.days) == status_filter
        ]

    total = len(all_treatments)
    pages = math.ceil(total / size) if total > 0 else 1

    # Paginate
    start = (page - 1) * size
    end = start + size
    page_items = all_treatments[start:end]

    items = [_treatment_to_response(t) for t in page_items]

    return TreatmentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Treatment).where(
            Treatment.id == treatment_id,
            Treatment.user_id == current_user.id,
            Treatment.deleted_at.is_(None),
        )
    )
    treatment = result.scalar_one_or_none()
    if treatment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment not found",
        )
    return _treatment_to_response(treatment)


@router.post("/", response_model=TreatmentResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment(
    data: TreatmentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    treatment = Treatment(
        user_id=current_user.id,
        date_start=data.date_start,
        name=data.name,
        days=data.days,
        receipt=data.receipt,
        body_region=data.body_region,
    )
    session.add(treatment)
    await session.commit()
    await session.refresh(treatment)
    return _treatment_to_response(treatment)


@router.put("/{treatment_id}", response_model=TreatmentResponse)
async def update_treatment(
    treatment_id: int,
    data: TreatmentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Treatment).where(
            Treatment.id == treatment_id,
            Treatment.user_id == current_user.id,
            Treatment.deleted_at.is_(None),
        )
    )
    treatment = result.scalar_one_or_none()
    if treatment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(treatment, field, value)

    await session.commit()
    await session.refresh(treatment)
    return _treatment_to_response(treatment)


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment(
    treatment_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Treatment).where(
            Treatment.id == treatment_id,
            Treatment.user_id == current_user.id,
            Treatment.deleted_at.is_(None),
        )
    )
    treatment = result.scalar_one_or_none()
    if treatment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Treatment not found",
        )

    treatment.deleted_at = datetime.utcnow()
    await session.commit()
    return None

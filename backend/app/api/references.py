from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models.reference import City, Clinic, Position, Procedure
from app.models.user import User
from app.models.visit import Visit
from app.schemas.reference import ReferenceCreate, ReferenceResponse, ReferenceUpdate


def create_reference_router(model_class, visit_fk_column: str) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=List[ReferenceResponse])
    async def list_items(
        search: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> List[ReferenceResponse]:
        stmt = select(model_class)
        if search:
            stmt = stmt.where(model_class.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(model_class.name)
        result = await session.execute(stmt)
        return result.scalars().all()

    @router.post("/", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
    async def create_item(
        data: ReferenceCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> ReferenceResponse:
        item = model_class(name=data.name)
        session.add(item)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Name already exists",
            )
        await session.refresh(item)
        return item

    @router.put("/{item_id}", response_model=ReferenceResponse)
    async def update_item(
        item_id: int,
        data: ReferenceUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> ReferenceResponse:
        result = await session.execute(
            select(model_class).where(model_class.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        item.name = data.name
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Name already exists",
            )
        await session.refresh(item)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        item_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> None:
        result = await session.execute(
            select(model_class).where(model_class.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )

        fk_col = getattr(Visit, visit_fk_column)
        count_result = await session.execute(
            select(func.count()).select_from(Visit).where(
                fk_col == item_id,
                Visit.deleted_at.is_(None),
            )
        )
        visit_count = count_result.scalar()
        if visit_count:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete: referenced by {visit_count} visit(s)",
            )

        await session.delete(item)
        await session.commit()

    return router


positions_router = create_reference_router(Position, "position_id")
procedures_router = create_reference_router(Procedure, "procedure_id")
clinics_router = create_reference_router(Clinic, "clinic_id")
cities_router = create_reference_router(City, "city_id")

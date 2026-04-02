from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.infrastructure.models.user import UserModel
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter()


def _user_to_profile(user: User) -> ProfileResponse:
    return ProfileResponse(
        sex=user.sex,
        date_of_birth=user.date_of_birth,
        height_cm=user.height_cm,
        weight_kg=float(user.weight_kg) if user.weight_kg is not None else None,
        blood_type=user.blood_type,
        allergies=user.allergies,
        chronic_conditions=user.chronic_conditions,
        emergency_contact_name=user.emergency_contact_name,
        emergency_contact_phone=user.emergency_contact_phone,
    )


@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return _user_to_profile(current_user)


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    values = {
        "sex": body.sex.value,
        "date_of_birth": body.date_of_birth,
        "height_cm": body.height_cm,
        "weight_kg": Decimal(str(body.weight_kg)) if body.weight_kg is not None else None,
        "blood_type": body.blood_type.value if body.blood_type is not None else None,
        "allergies": body.allergies,
        "chronic_conditions": body.chronic_conditions,
        "emergency_contact_name": body.emergency_contact_name,
        "emergency_contact_phone": body.emergency_contact_phone,
    }
    try:
        await session.execute(
            update(UserModel).where(UserModel.id == current_user.id).values(**values)
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Помилка оновлення профілю")

    # Return updated profile
    for key, val in values.items():
        setattr(current_user, key, val)
    return _user_to_profile(current_user)

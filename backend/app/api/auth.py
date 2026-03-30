import base64
import hashlib

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.database import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against Django PBKDF2 or bcrypt hash."""
    if stored_hash.startswith("pbkdf2_sha256$"):
        # Django PBKDF2-SHA256 format: pbkdf2_sha256$iterations$salt$hash
        parts = stored_hash.split("$")
        if len(parts) != 4:
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hash = parts[3]
        dk = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode(), salt.encode(), iterations
        )
        computed = base64.b64encode(dk).decode()
        return computed == expected_hash
    elif stored_hash.startswith("$2"):
        # bcrypt hash
        return bcrypt.checkpw(plain_password.encode(), stored_hash.encode())
    return False


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.username == body.username, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token: str, session: AsyncSession = Depends(get_session)):
    try:
        user_id = verify_token(token, expected_type="refresh")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    result = await session.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
    )

from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service, get_current_user
from app.application.auth_service import AuthAppService
from app.domain.entities import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, auth_service: AuthAppService = Depends(get_auth_service)):
    access, refresh = await auth_service.login(body.username, body.password)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token: str, auth_service: AuthAppService = Depends(get_auth_service)):
    access, refresh = await auth_service.refresh(token)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, username=current_user.username, is_active=current_user.is_active, sex=current_user.sex)

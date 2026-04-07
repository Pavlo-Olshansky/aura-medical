from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.infrastructure.repositories.push_repository import PushRepository
from app.infrastructure.vapid_manager import get_vapid_public_key
from app.schemas.push import SubscribeRequest, SubscribeResponse, UnsubscribeRequest, VapidKeyResponse

router = APIRouter()


@router.get("/vapid-key", response_model=VapidKeyResponse)
async def vapid_key(current_user: User = Depends(get_current_user)):
    return VapidKeyResponse(public_key=get_vapid_public_key())


@router.post("/subscribe", response_model=SubscribeResponse, status_code=201)
async def subscribe(
    body: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = PushRepository(session)
    is_new = await repo.save_subscription(
        user_id=current_user.id,
        endpoint=body.endpoint,
        p256dh_key=body.keys.p256dh,
        auth_key=body.keys.auth,
    )
    status = "subscribed" if is_new else "already_subscribed"
    return SubscribeResponse(status=status)


@router.delete("/subscribe", status_code=204)
async def unsubscribe(
    body: UnsubscribeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = PushRepository(session)
    await repo.delete_subscription_by_endpoint(body.endpoint)

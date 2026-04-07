import asyncio
import json
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.config import settings
from app.domain.entities import User
from app.infrastructure.database import get_session
from app.infrastructure.repositories.push_repository import PushRepository
from app.infrastructure.vapid_manager import get_vapid_keys, get_vapid_public_key
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


@router.get("/subscriptions")
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    repo = PushRepository(session)
    subs = await repo.get_subscriptions_for_user(current_user.id)
    return [{"endpoint": s.endpoint} for s in subs]


@router.get("/test-mode")
async def test_mode(current_user: User = Depends(get_current_user)):
    return {"test_mode": settings.TEST_MODE}


@router.post("/test", status_code=200)
async def test_push(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not settings.TEST_MODE:
        raise HTTPException(status_code=404, detail="Not found")

    repo = PushRepository(session)
    subs = await repo.get_subscriptions_for_user(current_user.id)
    if not subs:
        raise HTTPException(status_code=400, detail="Немає підписок на push")

    async def _send_delayed():
        await asyncio.sleep(30)
        from pywebpush import webpush, WebPushException

        vapid_keys = get_vapid_keys()
        payload = json.dumps({
            "title": "Тестове сповіщення",
            "body": "Push-нагадування працює!",
            "tag": "test-notification",
            "url": "/",
        })
        for sub in subs:
            parsed = urlparse(sub.endpoint)
            if not parsed.scheme or not parsed.netloc:
                continue  # skip dev placeholder subscriptions
            aud = f"{parsed.scheme}://{parsed.netloc}"
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                    },
                    data=payload,
                    vapid_private_key=vapid_keys["private_key"],
                    vapid_claims={"sub": settings.VAPID_MAILTO, "aud": aud},
                )
            except WebPushException:
                pass

    asyncio.create_task(_send_delayed())
    return {"status": "scheduled", "delay_seconds": 30}

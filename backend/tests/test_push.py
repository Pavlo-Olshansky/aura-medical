from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


@pytest.mark.asyncio
async def test_vapid_key(client, auth_headers):
    resp = await client.get("/api/v1/push/vapid-key", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "public_key" in data
    assert len(data["public_key"]) > 10


@pytest.mark.asyncio
async def test_subscribe(client, auth_headers):
    resp = await client.post(
        "/api/v1/push/subscribe",
        json={
            "endpoint": "https://push.example.com/test-1",
            "keys": {"p256dh": "test-p256dh-key", "auth": "test-auth-key"},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "subscribed"


@pytest.mark.asyncio
async def test_subscribe_duplicate(client, auth_headers):
    payload = {
        "endpoint": "https://push.example.com/test-dup",
        "keys": {"p256dh": "key1", "auth": "auth1"},
    }
    resp1 = await client.post("/api/v1/push/subscribe", json=payload, headers=auth_headers)
    assert resp1.status_code == 201
    assert resp1.json()["status"] == "subscribed"

    resp2 = await client.post("/api/v1/push/subscribe", json=payload, headers=auth_headers)
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "already_subscribed"


@pytest.mark.asyncio
async def test_unsubscribe(client, auth_headers):
    # Subscribe first
    await client.post(
        "/api/v1/push/subscribe",
        json={
            "endpoint": "https://push.example.com/test-unsub",
            "keys": {"p256dh": "k", "auth": "a"},
        },
        headers=auth_headers,
    )

    resp = await client.request(
        "DELETE",
        "/api/v1/push/subscribe",
        json={"endpoint": "https://push.example.com/test-unsub"},
        headers=auth_headers,
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_unsubscribe_idempotent(client, auth_headers):
    resp = await client.request(
        "DELETE",
        "/api/v1/push/subscribe",
        json={"endpoint": "https://push.example.com/nonexistent"},
        headers=auth_headers,
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_push_scheduler_sends_notification(session, test_user):
    from app.infrastructure.models.push_subscription import PushSubscriptionModel
    from app.infrastructure.models.visit import VisitModel

    # Create subscription
    sub = PushSubscriptionModel(
        user_id=test_user.id,
        endpoint="https://push.example.com/sched-test",
        p256dh_key="test-key",
        auth_key="test-auth",
    )
    session.add(sub)

    # Create future visit
    future_date = datetime.now(KYIV_TZ) + timedelta(hours=6)
    visit = VisitModel(user_id=test_user.id, date=future_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()

    with patch("app.application.push_scheduler.webpush") as mock_webpush, \
         patch("app.application.push_scheduler.async_session") as mock_session_factory:

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session_factory.return_value = mock_ctx

        from app.application.push_scheduler import send_push_reminders
        await send_push_reminders()

        assert mock_webpush.called
        call_kwargs = mock_webpush.call_args
        assert "https://push.example.com/sched-test" in str(call_kwargs)


@pytest.mark.asyncio
async def test_push_scheduler_handles_410(session, test_user):
    from pywebpush import WebPushException
    from app.infrastructure.models.push_subscription import PushSubscriptionModel
    from app.infrastructure.models.visit import VisitModel

    sub = PushSubscriptionModel(
        user_id=test_user.id,
        endpoint="https://push.example.com/expired",
        p256dh_key="test-key",
        auth_key="test-auth",
    )
    session.add(sub)

    future_date = datetime.now(KYIV_TZ) + timedelta(hours=6)
    visit = VisitModel(user_id=test_user.id, date=future_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()
    sub_id = sub.id

    mock_response = MagicMock()
    mock_response.status_code = 410

    with patch("app.application.push_scheduler.webpush") as mock_webpush, \
         patch("app.application.push_scheduler.async_session") as mock_session_factory:

        mock_webpush.side_effect = WebPushException("Gone", response=mock_response)

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=session)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_session_factory.return_value = mock_ctx

        from app.application.push_scheduler import send_push_reminders
        await send_push_reminders()

    # Subscription should be deleted
    from sqlalchemy import select
    result = await session.execute(
        select(PushSubscriptionModel).where(PushSubscriptionModel.id == sub_id)
    )
    assert result.scalar_one_or_none() is None

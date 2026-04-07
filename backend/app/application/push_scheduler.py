from __future__ import annotations

import json
from urllib.parse import urlparse

import structlog
from pywebpush import WebPushException, webpush

from app.application.notification_service import NotificationAppService
from app.config import settings
from app.infrastructure.database import async_session
from app.infrastructure.repositories.push_repository import PushRepository
from app.infrastructure.vapid_manager import get_vapid_keys

logger = structlog.get_logger()

REMINDER_BODY = {
    "day_before": "Нагадування за 1 день",
    "hour_before": "Нагадування за 1 годину",
}


async def send_push_reminders() -> None:
    """Scheduled task: send push notifications for upcoming reminders."""
    vapid_keys = get_vapid_keys()
    if not vapid_keys.get("private_key"):
        logger.warning("push_scheduler: no VAPID keys, skipping")
        return

    async with async_session() as session:
        push_repo = PushRepository(session)
        notification_svc = NotificationAppService(session)

        subscriptions = await push_repo.get_all_subscriptions_with_users()
        if not subscriptions:
            return

        # Group subscriptions by user
        user_subs: dict[int, list] = {}
        for sub in subscriptions:
            user_subs.setdefault(sub.user_id, []).append(sub)

        for user_id, subs in user_subs.items():
            reminders = await notification_svc.get_reminders(user_id)
            for reminder in reminders:
                already_sent = await push_repo.check_sent(
                    user_id,
                    reminder["entity_type"],
                    reminder["entity_id"],
                    reminder["reminder_type"],
                )
                if already_sent:
                    continue

                payload = json.dumps({
                    "title": reminder["title"],
                    "body": REMINDER_BODY.get(reminder["reminder_type"], "Нагадування"),
                    "tag": f"{reminder['entity_type']}-{reminder['entity_id']}-{reminder['reminder_type']}",
                    "url": reminder["route"],
                })

                for sub in subs:
                    try:
                        parsed = urlparse(sub.endpoint)
                        aud = f"{parsed.scheme}://{parsed.netloc}"
                        webpush(
                            subscription_info={
                                "endpoint": sub.endpoint,
                                "keys": {"p256dh": sub.p256dh_key, "auth": sub.auth_key},
                            },
                            data=payload,
                            vapid_private_key=vapid_keys["private_key"],
                            vapid_claims={"sub": settings.VAPID_MAILTO, "aud": aud},
                        )
                        logger.info(
                            "push_sent",
                            user_id=user_id,
                            entity=f"{reminder['entity_type']}/{reminder['entity_id']}",
                            type=reminder["reminder_type"],
                        )
                    except WebPushException as e:
                        if e.response and e.response.status_code == 410:
                            logger.info("push_subscription_expired", sub_id=sub.id)
                            await push_repo.delete_subscription_by_id(sub.id)
                        else:
                            logger.error("push_failed", sub_id=sub.id, error=str(e))

                await push_repo.log_sent(
                    user_id,
                    reminder["entity_type"],
                    reminder["entity_id"],
                    reminder["reminder_type"],
                )

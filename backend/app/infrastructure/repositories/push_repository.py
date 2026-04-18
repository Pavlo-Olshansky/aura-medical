from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.push_sent_log import PushSentLogModel
from app.infrastructure.models.push_subscription import PushSubscriptionModel


class PushRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_subscription(self, user_id: int, endpoint: str, p256dh_key: str, auth_key: str) -> bool:
        """Save or update subscription. Returns True if new, False if updated."""
        existing = await self._session.execute(
            select(PushSubscriptionModel).where(PushSubscriptionModel.endpoint == endpoint)
        )
        sub = existing.scalar_one_or_none()
        if sub:
            sub.user_id = user_id
            sub.p256dh_key = p256dh_key
            sub.auth_key = auth_key
            await self._session.commit()
            return False

        self._session.add(PushSubscriptionModel(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
        ))
        await self._session.commit()
        return True

    async def delete_subscription_by_endpoint(self, endpoint: str) -> None:
        result = await self._session.execute(
            select(PushSubscriptionModel).where(PushSubscriptionModel.endpoint == endpoint)
        )
        sub = result.scalar_one_or_none()
        if sub:
            await self._session.delete(sub)
            await self._session.commit()

    async def delete_subscription_by_id(self, sub_id: int) -> None:
        result = await self._session.execute(
            select(PushSubscriptionModel).where(PushSubscriptionModel.id == sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            await self._session.delete(sub)
            await self._session.commit()

    async def get_subscriptions_for_user(self, user_id: int) -> list[PushSubscriptionModel]:
        result = await self._session.execute(
            select(PushSubscriptionModel).where(PushSubscriptionModel.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_all_subscriptions_with_users(self) -> list[PushSubscriptionModel]:
        result = await self._session.execute(select(PushSubscriptionModel))
        return list(result.scalars().all())

    async def check_sent(self, user_id: int, entity_type: str, entity_id: int, reminder_type: str) -> bool:
        result = await self._session.execute(
            select(PushSentLogModel).where(
                PushSentLogModel.user_id == user_id,
                PushSentLogModel.entity_type == entity_type,
                PushSentLogModel.entity_id == entity_id,
                PushSentLogModel.reminder_type == reminder_type,
            )
        )
        return result.scalar_one_or_none() is not None

    async def log_sent(self, user_id: int, entity_type: str, entity_id: int, reminder_type: str) -> None:
        self._session.add(PushSentLogModel(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_type=reminder_type,
        ))
        await self._session.commit()

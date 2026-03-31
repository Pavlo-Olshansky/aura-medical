from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.infrastructure.models.user import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id, UserModel.is_active.is_(True))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == username, UserModel.is_active.is_(True))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            is_active=model.is_active,
        )

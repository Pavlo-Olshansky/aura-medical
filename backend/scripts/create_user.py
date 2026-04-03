"""Create a user with given credentials. Usage: python -m scripts.create_user <username> <password>"""
import asyncio
import sys

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import async_session, engine
from app.infrastructure.models.user import UserModel


async def create_user(username: str, password: str) -> None:
    async with async_session() as session:
        existing = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        if existing.scalar_one_or_none():
            print(f"User '{username}' already exists, skipping.")
            return

        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = UserModel(username=username, password_hash=pw_hash, is_active=True)
        session.add(user)
        await session.commit()
        print(f"User '{username}' created.")

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_user <username> <password>")
        sys.exit(1)
    asyncio.run(create_user(sys.argv[1], sys.argv[2]))

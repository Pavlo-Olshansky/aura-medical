"""Create a user and seed reference data. Usage: python -m scripts.create_user <username> <password>"""
import asyncio
import sys

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import async_session, engine
from app.infrastructure.models.user import UserModel
from app.infrastructure.models.reference import PositionModel, ProcedureModel, ClinicModel, CityModel

CITIES = [
    "Київ",
    "Харків",
    "Одеса",
    "Дніпро",
    "Львів",
]

CLINICS = [
    "Добробут",
    "Борис",
    "Оберіг",
    "Медіком",
    "Ісіда",
    "Universum Clinic",
    "Інто-Сана",
    "Адоніс",
    "Eurolab",
    "Медікавер",
]

POSITIONS = [
    "Терапевт",
    "Кардіолог",
    "Невролог",
    "Офтальмолог",
    "ЛОР",
    "Дерматолог",
    "Стоматолог",
    "Хірург",
    "Ендокринолог",
    "Гастроентеролог",
    "Уролог",
    "Ортопед",
    "Гінеколог",
    "Пульмонолог",
    "Алерголог",
]

PROCEDURES = [
    "Консультація",
    "Огляд",
    "УЗД",
    "Аналізи",
    "ЕКГ",
    "Рентген",
    "МРТ",
    "КТ",
    "Вакцинація",
    "Операція",
    "Фізіотерапія",
    "Ендоскопія",
]


async def seed_references(session: AsyncSession) -> None:
    for model_class, items in [
        (CityModel, CITIES),
        (ClinicModel, CLINICS),
        (PositionModel, POSITIONS),
        (ProcedureModel, PROCEDURES),
    ]:
        existing = await session.execute(select(model_class.name))
        existing_names = {row[0] for row in existing.all()}
        added = 0
        for name in items:
            if name not in existing_names:
                session.add(model_class(name=name))
                added += 1
        if added:
            await session.commit()
            print(f"  {model_class.__tablename__}: added {added} items")
        else:
            print(f"  {model_class.__tablename__}: all items exist")


async def create_user(username: str, password: str) -> None:
    async with async_session() as session:
        # Create user
        existing = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        if existing.scalar_one_or_none():
            print(f"User '{username}' already exists, skipping.")
        else:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = UserModel(username=username, password_hash=pw_hash, is_active=True)
            session.add(user)
            await session.commit()
            print(f"User '{username}' created.")

        # Seed references
        print("Seeding reference data...")
        await seed_references(session)

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_user <username> <password>")
        sys.exit(1)
    asyncio.run(create_user(sys.argv[1], sys.argv[2]))

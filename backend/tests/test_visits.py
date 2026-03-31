from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City, Clinic, Position, Procedure, Visit


@pytest_asyncio.fixture
async def position(session: AsyncSession) -> Position:
    obj = Position(name="Терапевт")
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest_asyncio.fixture
async def procedure(session: AsyncSession) -> Procedure:
    obj = Procedure(name="Огляд")
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest_asyncio.fixture
async def clinic(session: AsyncSession) -> Clinic:
    obj = Clinic(name="Клініка Здоров'я")
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest_asyncio.fixture
async def city(session: AsyncSession) -> City:
    obj = City(name="Київ")
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest.mark.asyncio
async def test_create_visit(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    position: Position,
    procedure: Procedure,
    clinic: Clinic,
    city: City,
):
    response = await client.post(
        "/api/visits/",
        headers=auth_headers,
        data={
            "date": "2026-03-15T10:00:00",
            "position_id": str(position.id),
            "doctor": "Іванов І.І.",
            "procedure_id": str(procedure.id),
            "procedure_details": "Загальний огляд",
            "clinic_id": str(clinic.id),
            "city_id": str(city.id),
            "comment": "Все добре",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["doctor"] == "Іванов І.І."
    assert data["position"]["id"] == position.id
    assert data["position"]["name"] == "Терапевт"
    assert data["procedure"]["id"] == procedure.id
    assert data["clinic"]["id"] == clinic.id
    assert data["city"]["id"] == city.id
    assert data["comment"] == "Все добре"
    assert data["has_document"] is False
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_visits_paginated(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    session: AsyncSession,
):
    for i in range(5):
        visit = Visit(
            user_id=test_user.id,
            date=datetime(2026, 3, 10 + i, 10, 0, 0),
        )
        session.add(visit)
    await session.commit()

    response = await client.get(
        "/api/visits/",
        headers=auth_headers,
        params={"page": 1, "size": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["pages"] == 3


@pytest.mark.asyncio
async def test_get_visit_detail(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    position: Position,
    procedure: Procedure,
    clinic: Clinic,
    city: City,
    session: AsyncSession,
):
    visit = Visit(
        user_id=test_user.id,
        date=datetime(2026, 3, 15, 10, 0, 0),
        position_id=position.id,
        doctor="Іванов І.І.",
        procedure_id=procedure.id,
        clinic_id=clinic.id,
        city_id=city.id,
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    response = await client.get(
        f"/api/visits/{visit.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == visit.id
    assert data["doctor"] == "Іванов І.І."
    assert data["position"]["name"] == "Терапевт"
    assert data["procedure"]["name"] == "Огляд"
    assert data["clinic"]["name"] == "Клініка Здоров'я"
    assert data["city"]["name"] == "Київ"


@pytest.mark.asyncio
async def test_update_visit(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    session: AsyncSession,
):
    visit = Visit(
        user_id=test_user.id,
        date=datetime(2026, 3, 15, 10, 0, 0),
        doctor="Іванов І.І.",
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    response = await client.put(
        f"/api/visits/{visit.id}",
        headers=auth_headers,
        data={
            "doctor": "Петров П.П.",
            "comment": "Оновлений коментар",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["doctor"] == "Петров П.П."
    assert data["comment"] == "Оновлений коментар"


@pytest.mark.asyncio
async def test_soft_delete_visit(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    session: AsyncSession,
):
    visit = Visit(
        user_id=test_user.id,
        date=datetime(2026, 3, 15, 10, 0, 0),
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    response = await client.delete(
        f"/api/visits/{visit.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    response = await client.get(
        f"/api/visits/{visit.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_visits_by_date(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
    session: AsyncSession,
):
    visit1 = Visit(user_id=test_user.id, date=datetime(2026, 1, 10, 10, 0, 0))
    visit2 = Visit(user_id=test_user.id, date=datetime(2026, 3, 15, 10, 0, 0))
    visit3 = Visit(user_id=test_user.id, date=datetime(2026, 6, 20, 10, 0, 0))
    session.add_all([visit1, visit2, visit3])
    await session.commit()

    response = await client.get(
        "/api/visits/",
        headers=auth_headers,
        params={"date_from": "2026-03-01", "date_to": "2026-04-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_visit_not_found(
    client: AsyncClient,
    auth_headers: dict,
    test_user,
):
    response = await client.get(
        "/api/visits/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Visit not found"

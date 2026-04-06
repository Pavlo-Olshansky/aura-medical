from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.reference import CityModel, ClinicModel, PositionModel, ProcedureModel
from app.infrastructure.models.user import UserModel
from app.infrastructure.models.visit import VisitModel


@pytest.mark.asyncio
async def test_create_position(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/positions/",
        json={"name": "Терапевт"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Терапевт"
    assert "id" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_list_positions_with_search(client: AsyncClient, auth_headers: dict, session: AsyncSession):
    pos1 = PositionModel(name="Терапевт")
    pos2 = PositionModel(name="Хірург")
    pos3 = PositionModel(name="Кардіолог")
    session.add_all([pos1, pos2, pos3])
    await session.commit()

    # List all
    response = await client.get("/api/v1/positions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Search
    response = await client.get(
        "/api/v1/positions/", params={"search": "Терап"}, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Терапевт"


@pytest.mark.asyncio
async def test_update_position(client: AsyncClient, auth_headers: dict, session: AsyncSession):
    pos = PositionModel(name="Терапевт")
    session.add(pos)
    await session.commit()
    await session.refresh(pos)

    response = await client.put(
        f"/api/v1/positions/{pos.id}",
        json={"name": "Лікар-терапевт"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Лікар-терапевт"
    assert data["id"] == pos.id


@pytest.mark.asyncio
async def test_delete_position(client: AsyncClient, auth_headers: dict, session: AsyncSession):
    pos = PositionModel(name="Терапевт")
    session.add(pos)
    await session.commit()
    await session.refresh(pos)

    response = await client.delete(
        f"/api/v1/positions/{pos.id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify deleted
    response = await client.get("/api/v1/positions/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_delete_position_referenced_by_visit(
    client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: UserModel
):
    pos = PositionModel(name="Терапевт")
    session.add(pos)
    await session.commit()
    await session.refresh(pos)

    visit = VisitModel(
        user_id=test_user.id,
        date=datetime.now(timezone.utc),
        position_id=pos.id,
    )
    session.add(visit)
    await session.commit()

    response = await client.delete(
        f"/api/v1/positions/{pos.id}", headers=auth_headers
    )
    assert response.status_code == 409
    assert "referenced by 1 visit(s)" in response.json()["detail"]


@pytest.mark.asyncio
async def test_duplicate_name_returns_409(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/positions/",
        json={"name": "Терапевт"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/positions/",
        json={"name": "Терапевт"},
        headers=auth_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Name already exists"


@pytest.mark.asyncio
async def test_crud_clinics(client: AsyncClient, auth_headers: dict, session: AsyncSession):
    # Create
    response = await client.post(
        "/api/v1/clinics/",
        json={"name": "Клініка Борис"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    clinic_id = response.json()["id"]

    # List
    response = await client.get("/api/v1/clinics/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Update
    response = await client.put(
        f"/api/v1/clinics/{clinic_id}",
        json={"name": "Клініка Добробут"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Клініка Добробут"

    # Delete
    response = await client.delete(
        f"/api/v1/clinics/{clinic_id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify deleted
    response = await client.get("/api/v1/clinics/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

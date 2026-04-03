from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


@pytest.mark.asyncio
async def test_create_vaccination(
    client: AsyncClient, auth_headers: dict, test_user,
):
    response = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2026-03-15T10:00:00",
            "vaccine_name": "COVID-19 Pfizer",
            "manufacturer": "Pfizer-BioNTech",
            "lot_number": "EL9261",
            "dose_number": "1",
            "next_due_date": "2026-04-15T10:00:00",
            "notes": "Перша доза",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["vaccine_name"] == "COVID-19 Pfizer"
    assert data["manufacturer"] == "Pfizer-BioNTech"
    assert data["lot_number"] == "EL9261"
    assert data["dose_number"] == 1
    assert data["notes"] == "Перша доза"
    assert data["has_document"] is False
    assert "id" in data
    assert "status" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_list_vaccinations(
    client: AsyncClient, auth_headers: dict, test_user,
):
    # Create two vaccinations
    for i in range(2):
        await client.post(
            "/api/v1/vaccinations/",
            data={
                "date": f"2026-03-{15+i}T10:00:00",
                "vaccine_name": f"Вакцина {i}",
                "dose_number": "1",
            },
            headers=auth_headers,
        )

    response = await client.get("/api/v1/vaccinations/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert "status" in data["items"][0]
    assert "page" in data
    assert "size" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_update_vaccination(
    client: AsyncClient, auth_headers: dict, test_user,
):
    # Create
    create_resp = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2026-03-15T10:00:00",
            "vaccine_name": "Грип",
            "dose_number": "1",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    vacc_id = create_resp.json()["id"]

    # Update
    response = await client.put(
        f"/api/v1/vaccinations/{vacc_id}",
        data={
            "vaccine_name": "Грип (оновлено)",
            "notes": "Оновлений запис",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vaccine_name"] == "Грип (оновлено)"
    assert data["notes"] == "Оновлений запис"


@pytest.mark.asyncio
async def test_delete_vaccination(
    client: AsyncClient, auth_headers: dict, test_user,
):
    # Create
    create_resp = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2026-03-15T10:00:00",
            "vaccine_name": "Гепатит B",
            "dose_number": "1",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    vacc_id = create_resp.json()["id"]

    # Delete (soft)
    response = await client.delete(
        f"/api/v1/vaccinations/{vacc_id}", headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify it no longer appears
    response = await client.get(
        f"/api/v1/vaccinations/{vacc_id}", headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_vaccination_status_upcoming(
    client: AsyncClient, auth_headers: dict, test_user,
):
    future_date = (datetime.now(KYIV_TZ) + timedelta(days=30)).isoformat()
    response = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2026-03-15T10:00:00",
            "vaccine_name": "COVID-19 бустер",
            "dose_number": "3",
            "next_due_date": future_date,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "upcoming"


@pytest.mark.asyncio
async def test_vaccination_status_overdue(
    client: AsyncClient, auth_headers: dict, test_user,
):
    past_date = (datetime.now(KYIV_TZ) - timedelta(days=30)).isoformat()
    response = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2025-01-15T10:00:00",
            "vaccine_name": "Правець",
            "dose_number": "1",
            "next_due_date": past_date,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "overdue"


@pytest.mark.asyncio
async def test_vaccination_status_completed(
    client: AsyncClient, auth_headers: dict, test_user,
):
    response = await client.post(
        "/api/v1/vaccinations/",
        data={
            "date": "2026-03-15T10:00:00",
            "vaccine_name": "Кір-краснуха-паротит",
            "dose_number": "2",
            # No next_due_date -> status = completed
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"

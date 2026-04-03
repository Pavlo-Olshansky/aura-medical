from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Treatment, User

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


def _make_treatment_payload(
    date_start: datetime = None,
    name: str = "Амоксицилін",
    days: int = 10,
    receipt: str = "500мг 3 рази на день",
):
    if date_start is None:
        date_start = datetime.now(KYIV_TZ)
    return {
        "date_start": date_start.isoformat(),
        "name": name,
        "days": days,
        "receipt": receipt,
    }


@pytest.mark.asyncio
async def test_create_treatment(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = _make_treatment_payload()
    response = await client.post(
        "/api/v1/treatments/", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Амоксицилін"
    assert data["days"] == 10
    assert data["receipt"] == "500мг 3 рази на день"
    assert "id" in data
    assert "status" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_list_treatments(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    # Create two treatments
    for i in range(2):
        payload = _make_treatment_payload(name=f"Treatment {i}")
        await client.post(
            "/api/v1/treatments/", json=payload, headers=auth_headers
        )

    response = await client.get("/api/v1/treatments/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_treatment_status_active(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    now = datetime.now(KYIV_TZ)
    payload = _make_treatment_payload(date_start=now, days=10)
    response = await client.post(
        "/api/v1/treatments/", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_treatment_status_completed(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    past = datetime.now(KYIV_TZ) - timedelta(days=30)
    payload = _make_treatment_payload(date_start=past, days=5)
    response = await client.post(
        "/api/v1/treatments/", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_soft_delete_treatment(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    payload = _make_treatment_payload()
    create_resp = await client.post(
        "/api/v1/treatments/", json=payload, headers=auth_headers
    )
    assert create_resp.status_code == 201
    treatment_id = create_resp.json()["id"]

    # Delete
    delete_resp = await client.delete(
        f"/api/v1/treatments/{treatment_id}", headers=auth_headers
    )
    assert delete_resp.status_code == 204

    # Confirm it no longer appears
    get_resp = await client.get(
        f"/api/v1/treatments/{treatment_id}", headers=auth_headers
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_status(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    # Create an active treatment (starting today, 10 days)
    now = datetime.now(KYIV_TZ)
    active_payload = _make_treatment_payload(
        date_start=now, name="Active Treatment", days=10
    )
    await client.post(
        "/api/v1/treatments/", json=active_payload, headers=auth_headers
    )

    # Create a completed treatment (started 30 days ago, 5 days)
    past = now - timedelta(days=30)
    completed_payload = _make_treatment_payload(
        date_start=past, name="Completed Treatment", days=5
    )
    await client.post(
        "/api/v1/treatments/", json=completed_payload, headers=auth_headers
    )

    # Filter active
    active_resp = await client.get(
        "/api/v1/treatments/", params={"status": "active"}, headers=auth_headers
    )
    assert active_resp.status_code == 200
    active_data = active_resp.json()
    assert all(item["status"] == "active" for item in active_data["items"])
    assert active_data["total"] >= 1

    # Filter completed
    completed_resp = await client.get(
        "/api/v1/treatments/",
        params={"status": "completed"},
        headers=auth_headers,
    )
    assert completed_resp.status_code == 200
    completed_data = completed_resp.json()
    assert all(
        item["status"] == "completed" for item in completed_data["items"]
    )
    assert completed_data["total"] >= 1

from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.models.treatment import Treatment, KYIV_TZ
from app.models.visit import Visit


@pytest_asyncio.fixture
async def visits_with_regions(session, test_user):
    now = datetime.now(KYIV_TZ)
    visits = [
        Visit(user_id=test_user.id, date=now - timedelta(days=i), body_region="chest")
        for i in range(3)
    ]
    visits.append(Visit(user_id=test_user.id, date=now - timedelta(days=10), body_region="eyes"))
    visits.append(Visit(user_id=test_user.id, date=now - timedelta(days=5), body_region="whole_body"))
    visits.append(Visit(user_id=test_user.id, date=now - timedelta(days=1), body_region=None))
    for v in visits:
        session.add(v)
    await session.commit()
    return visits


@pytest_asyncio.fixture
async def treatment_with_region(session, test_user):
    now = datetime.now(KYIV_TZ)
    t = Treatment(
        user_id=test_user.id,
        date_start=now - timedelta(days=5),
        name="Аспірін",
        days=30,
        receipt="1 таб/день",
        body_region="chest",
    )
    session.add(t)
    await session.commit()
    return t


@pytest.mark.asyncio
async def test_body_map_summary(client, auth_headers, visits_with_regions, treatment_with_region):
    response = await client.get("/api/dashboard/body-map/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "regions" in data
    assert "unmapped_visit_count" in data
    assert "whole_body_visit_count" in data

    assert data["unmapped_visit_count"] == 1
    assert data["whole_body_visit_count"] == 1

    chest = data["regions"].get("chest")
    assert chest is not None
    assert chest["visit_count"] == 3
    assert chest["active_treatment_count"] == 1

    eyes = data["regions"].get("eyes")
    assert eyes is not None
    assert eyes["visit_count"] == 1


@pytest.mark.asyncio
async def test_body_map_summary_empty(client, auth_headers, test_user):
    response = await client.get("/api/dashboard/body-map/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["regions"] == {}
    assert data["unmapped_visit_count"] == 0
    assert data["whole_body_visit_count"] == 0


@pytest.mark.asyncio
async def test_body_map_detail(client, auth_headers, visits_with_regions, treatment_with_region):
    response = await client.get("/api/dashboard/body-map/chest/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["region"] == "chest"
    assert data["label"] == "Грудна клітка"
    assert len(data["visits"]) == 3
    assert len(data["treatments"]) == 1
    assert data["treatments"][0]["name"] == "Аспірін"
    assert data["treatments"][0]["status"] == "active"
    assert "date_end" in data["treatments"][0]


@pytest.mark.asyncio
async def test_body_map_detail_invalid_region(client, auth_headers, test_user):
    response = await client.get("/api/dashboard/body-map/invalid_region/", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_body_map_detail_pagination(client, auth_headers, visits_with_regions):
    response = await client.get("/api/dashboard/body-map/chest/?limit=2&offset=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["visits"]) == 2

    response2 = await client.get("/api/dashboard/body-map/chest/?limit=2&offset=2", headers=auth_headers)
    data2 = response2.json()
    assert len(data2["visits"]) == 1


@pytest.mark.asyncio
async def test_body_map_requires_auth(client):
    response = await client.get("/api/dashboard/body-map/")
    assert response.status_code == 401

    response2 = await client.get("/api/dashboard/body-map/chest/")
    assert response2.status_code == 401

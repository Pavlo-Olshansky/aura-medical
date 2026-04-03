from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.visit import VisitModel


@pytest_asyncio.fixture
async def visit(session: AsyncSession, test_user) -> VisitModel:
    obj = VisitModel(
        user_id=test_user.id,
        date=datetime.now(timezone.utc),
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest.mark.asyncio
async def test_create_lab_result(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    response = await client.post(
        "/api/v1/lab-results/",
        json={
            "date": "2026-03-20T10:00:00+02:00",
            "visit_id": visit.id,
            "notes": "Загальний аналіз крові",
            "entries": [
                {
                    "biomarker_name": "Гемоглобін",
                    "value": "145",
                    "unit": "г/л",
                    "ref_min": "130",
                    "ref_max": "170",
                },
                {
                    "biomarker_name": "Лейкоцити",
                    "value": "12.5",
                    "unit": "×10⁹/л",
                    "ref_min": "4.0",
                    "ref_max": "9.0",
                },
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["visit_id"] == visit.id
    assert data["notes"] == "Загальний аналіз крові"
    assert len(data["entries"]) == 2
    assert data["entries"][0]["biomarker_name"] == "Гемоглобін"
    assert data["entries"][0]["is_normal"] is True
    assert data["entries"][1]["biomarker_name"] == "Лейкоцити"
    assert data["entries"][1]["is_normal"] is False  # 12.5 > 9.0
    assert "id" in data


@pytest.mark.asyncio
async def test_get_lab_result(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    # Create first
    create_resp = await client.post(
        "/api/v1/lab-results/",
        json={
            "date": "2026-03-20T10:00:00+02:00",
            "visit_id": visit.id,
            "entries": [
                {
                    "biomarker_name": "Глюкоза",
                    "value": "5.1",
                    "unit": "ммоль/л",
                    "ref_min": "3.9",
                    "ref_max": "5.5",
                },
            ],
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    lab_result_id = create_resp.json()["id"]

    # Get detail
    response = await client.get(
        f"/api/v1/lab-results/{lab_result_id}", headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lab_result_id
    assert len(data["entries"]) == 1
    assert data["entries"][0]["biomarker_name"] == "Глюкоза"


@pytest.mark.asyncio
async def test_list_lab_results(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    # Create two lab results
    for i in range(2):
        await client.post(
            "/api/v1/lab-results/",
            json={
                "date": f"2026-03-{20+i}T10:00:00+02:00",
                "entries": [
                    {
                        "biomarker_name": f"Маркер {i}",
                        "value": "5.0",
                        "unit": "мг/л",
                        "ref_min": "1.0",
                        "ref_max": "10.0",
                    },
                    {
                        "biomarker_name": f"Маркер поза нормою {i}",
                        "value": "15.0",
                        "unit": "мг/л",
                        "ref_min": "1.0",
                        "ref_max": "10.0",
                    },
                ],
            },
            headers=auth_headers,
        )

    response = await client.get(
        "/api/v1/lab-results/",
        headers=auth_headers,
        params={"page": 1, "size": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert "entries_count" in data["items"][0]
    assert "out_of_range_count" in data["items"][0]
    assert data["items"][0]["entries_count"] == 2
    assert data["items"][0]["out_of_range_count"] == 1


@pytest.mark.asyncio
async def test_update_lab_result(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    # Create
    create_resp = await client.post(
        "/api/v1/lab-results/",
        json={
            "date": "2026-03-20T10:00:00+02:00",
            "entries": [
                {
                    "biomarker_name": "Гемоглобін",
                    "value": "145",
                    "unit": "г/л",
                },
            ],
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    lab_result_id = create_resp.json()["id"]

    # Update — replace entries
    response = await client.put(
        f"/api/v1/lab-results/{lab_result_id}",
        json={
            "notes": "Оновлені результати",
            "entries": [
                {
                    "biomarker_name": "Глюкоза",
                    "value": "4.8",
                    "unit": "ммоль/л",
                    "ref_min": "3.9",
                    "ref_max": "5.5",
                },
                {
                    "biomarker_name": "Креатинін",
                    "value": "80",
                    "unit": "мкмоль/л",
                    "ref_min": "62",
                    "ref_max": "106",
                },
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Оновлені результати"
    assert len(data["entries"]) == 2
    names = [e["biomarker_name"] for e in data["entries"]]
    assert "Глюкоза" in names
    assert "Креатинін" in names


@pytest.mark.asyncio
async def test_delete_lab_result(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    # Create
    create_resp = await client.post(
        "/api/v1/lab-results/",
        json={
            "date": "2026-03-20T10:00:00+02:00",
            "entries": [
                {
                    "biomarker_name": "Гемоглобін",
                    "value": "145",
                    "unit": "г/л",
                },
            ],
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    lab_result_id = create_resp.json()["id"]

    # Delete (soft)
    response = await client.delete(
        f"/api/v1/lab-results/{lab_result_id}", headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify it's gone from GET
    response = await client.get(
        f"/api/v1/lab-results/{lab_result_id}", headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_biomarker_trend(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    # Create multiple lab results with same biomarker at different dates
    dates = [
        "2026-01-15T10:00:00+02:00",
        "2026-02-15T10:00:00+02:00",
        "2026-03-15T10:00:00+02:00",
    ]
    values = ["130", "140", "150"]
    for date_str, value in zip(dates, values):
        await client.post(
            "/api/v1/lab-results/",
            json={
                "date": date_str,
                "entries": [
                    {
                        "biomarker_name": "Гемоглобін",
                        "value": value,
                        "unit": "г/л",
                        "ref_min": "130",
                        "ref_max": "170",
                    },
                ],
            },
            headers=auth_headers,
        )

    response = await client.get(
        "/api/v1/lab-results/biomarker-trend",
        params={"biomarker_name": "Гемоглобін"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["biomarker_name"] == "Гемоглобін"
    assert len(data["data_points"]) == 3


@pytest.mark.asyncio
async def test_out_of_range_computed(
    client: AsyncClient, auth_headers: dict, test_user, visit: VisitModel,
):
    response = await client.post(
        "/api/v1/lab-results/",
        json={
            "date": "2026-03-20T10:00:00+02:00",
            "entries": [
                {
                    "biomarker_name": "Гемоглобін",
                    "value": "110",
                    "unit": "г/л",
                    "ref_min": "130",
                    "ref_max": "170",
                },
                {
                    "biomarker_name": "Глюкоза",
                    "value": "4.5",
                    "unit": "ммоль/л",
                    "ref_min": "3.9",
                    "ref_max": "5.5",
                },
                {
                    "biomarker_name": "Тест без норми",
                    "value": "42",
                    "unit": "од",
                },
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    entries = {e["biomarker_name"]: e for e in data["entries"]}

    # 110 < 130 -> out of range
    assert entries["Гемоглобін"]["is_normal"] is False
    # 4.5 is within [3.9, 5.5] -> normal
    assert entries["Глюкоза"]["is_normal"] is True
    # No ref range -> None
    assert entries["Тест без норми"]["is_normal"] is None

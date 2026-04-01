from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.metric_type import MetricTypeModel


@pytest_asyncio.fixture
async def metric_type_simple(session: AsyncSession) -> MetricTypeModel:
    """A simple metric type without secondary value (e.g. pulse)."""
    obj = MetricTypeModel(
        name="Пульс", unit="уд/хв", has_secondary_value=False,
        ref_min=60, ref_max=100, sort_order=1,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest_asyncio.fixture
async def metric_type_bp(session: AsyncSession) -> MetricTypeModel:
    """Blood pressure metric type with secondary value."""
    obj = MetricTypeModel(
        name="Артеріальний тиск", unit="мм рт.ст.", has_secondary_value=True,
        ref_min=90, ref_max=120, ref_min_secondary=60, ref_max_secondary=80,
        sort_order=2,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@pytest.mark.asyncio
async def test_create_health_metric(
    client: AsyncClient, auth_headers: dict, test_user,
    metric_type_simple: MetricTypeModel,
):
    response = await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_simple.id,
            "date": "2026-03-20T08:00:00+02:00",
            "value": "72",
            "notes": "Ранковий вимір",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metric_type_id"] == metric_type_simple.id
    assert data["metric_type"]["name"] == "Пульс"
    assert float(data["value"]) == 72.0
    assert data["notes"] == "Ранковий вимір"
    assert data["secondary_value"] is None
    assert "id" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_create_blood_pressure(
    client: AsyncClient, auth_headers: dict, test_user,
    metric_type_bp: MetricTypeModel,
):
    # Blood pressure requires secondary_value
    response = await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_bp.id,
            "date": "2026-03-20T08:00:00+02:00",
            "value": "120",
            "secondary_value": "80",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert float(data["value"]) == 120.0
    assert float(data["secondary_value"]) == 80.0
    assert data["metric_type"]["has_secondary_value"] is True

    # Without secondary_value should fail for BP type
    response = await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_bp.id,
            "date": "2026-03-20T09:00:00+02:00",
            "value": "120",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_health_metrics(
    client: AsyncClient, auth_headers: dict, test_user,
    metric_type_simple: MetricTypeModel, metric_type_bp: MetricTypeModel,
):
    # Create metrics of different types
    await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_simple.id,
            "date": "2026-03-20T08:00:00+02:00",
            "value": "72",
        },
        headers=auth_headers,
    )
    await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_bp.id,
            "date": "2026-03-20T08:00:00+02:00",
            "value": "120",
            "secondary_value": "80",
        },
        headers=auth_headers,
    )

    # List all
    response = await client.get("/api/health-metrics/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

    # Filter by metric_type_id
    response = await client.get(
        "/api/health-metrics/",
        params={"metric_type_id": metric_type_simple.id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["metric_type_id"] == metric_type_simple.id


@pytest.mark.asyncio
async def test_delete_health_metric(
    client: AsyncClient, auth_headers: dict, test_user,
    metric_type_simple: MetricTypeModel,
):
    # Create
    create_resp = await client.post(
        "/api/health-metrics/",
        json={
            "metric_type_id": metric_type_simple.id,
            "date": "2026-03-20T08:00:00+02:00",
            "value": "72",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    metric_id = create_resp.json()["id"]

    # Delete (hard)
    response = await client.delete(
        f"/api/health-metrics/{metric_id}", headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify 404 on subsequent GET
    response = await client.get(
        f"/api/health-metrics/{metric_id}", headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_trend(
    client: AsyncClient, auth_headers: dict, test_user,
    metric_type_simple: MetricTypeModel,
):
    # Create multiple data points
    dates = [
        "2026-01-10T08:00:00+02:00",
        "2026-02-10T08:00:00+02:00",
        "2026-03-10T08:00:00+02:00",
    ]
    values = ["68", "72", "75"]
    for date_str, value in zip(dates, values):
        await client.post(
            "/api/health-metrics/",
            json={
                "metric_type_id": metric_type_simple.id,
                "date": date_str,
                "value": value,
            },
            headers=auth_headers,
        )

    response = await client.get(
        "/api/health-metrics/trend",
        params={"metric_type_id": metric_type_simple.id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metric_type"] == "Пульс"
    assert data["unit"] == "уд/хв"
    assert len(data["data_points"]) == 3

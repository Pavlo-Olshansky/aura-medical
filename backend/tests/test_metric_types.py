from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.health_metric import HealthMetricModel
from app.infrastructure.models.metric_type import MetricTypeModel


SEED_METRIC_TYPES = [
    {"name": "Артеріальний тиск", "unit": "мм рт.ст.", "has_secondary_value": True,
     "ref_min": 90, "ref_max": 120, "ref_min_secondary": 60, "ref_max_secondary": 80, "sort_order": 1},
    {"name": "Пульс", "unit": "уд/хв", "has_secondary_value": False,
     "ref_min": 60, "ref_max": 100, "sort_order": 2},
    {"name": "Температура тіла", "unit": "°C", "has_secondary_value": False,
     "ref_min": 35.5, "ref_max": 37.0, "sort_order": 3},
    {"name": "Вага", "unit": "кг", "has_secondary_value": False, "sort_order": 4},
    {"name": "Глюкоза крові", "unit": "ммоль/л", "has_secondary_value": False,
     "ref_min": 3.3, "ref_max": 5.5, "sort_order": 5},
    {"name": "Сатурація кисню (SpO2)", "unit": "%", "has_secondary_value": False,
     "ref_min": 95, "ref_max": 100, "sort_order": 6},
    {"name": "Частота дихання", "unit": "дих/хв", "has_secondary_value": False,
     "ref_min": 12, "ref_max": 20, "sort_order": 7},
]


@pytest_asyncio.fixture
async def seed_metric_types(session: AsyncSession):
    """Insert 7 seed metric types matching production seed data."""
    for data in SEED_METRIC_TYPES:
        obj = MetricTypeModel(**data)
        session.add(obj)
    await session.commit()


@pytest.mark.asyncio
async def test_list_metric_types(
    client: AsyncClient, auth_headers: dict, seed_metric_types,
):
    response = await client.get("/api/v1/metric-types/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7


@pytest.mark.asyncio
async def test_create_metric_type(
    client: AsyncClient, auth_headers: dict,
):
    response = await client.post(
        "/api/v1/metric-types/",
        json={
            "name": "Індекс маси тіла",
            "unit": "кг/м²",
            "has_secondary_value": False,
            "ref_min": "18.5",
            "ref_max": "24.9",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Індекс маси тіла"
    assert data["unit"] == "кг/м²"
    assert data["has_secondary_value"] is False
    assert "id" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_update_metric_type(
    client: AsyncClient, auth_headers: dict, session: AsyncSession,
):
    obj = MetricTypeModel(
        name="Тестовий тип", unit="од", has_secondary_value=False, sort_order=0,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    response = await client.put(
        f"/api/v1/metric-types/{obj.id}",
        json={"name": "Оновлений тип", "unit": "нова од"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Оновлений тип"
    assert data["unit"] == "нова од"
    assert data["id"] == obj.id


@pytest.mark.asyncio
async def test_delete_metric_type(
    client: AsyncClient, auth_headers: dict, session: AsyncSession,
):
    obj = MetricTypeModel(
        name="Для видалення", unit="од", has_secondary_value=False, sort_order=0,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    response = await client.delete(
        f"/api/v1/metric-types/{obj.id}", headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify deleted
    response = await client.get("/api/v1/metric-types/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_delete_in_use_returns_409(
    client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user,
):
    # Create a metric type
    mt = MetricTypeModel(
        name="Тип у використанні", unit="од", has_secondary_value=False, sort_order=0,
    )
    session.add(mt)
    await session.commit()
    await session.refresh(mt)

    # Create a health metric referencing the type
    metric = HealthMetricModel(
        user_id=test_user.id,
        metric_type_id=mt.id,
        date=datetime.now(timezone.utc),
        value=72,
    )
    session.add(metric)
    await session.commit()

    # Try to delete — should fail with 409
    response = await client.delete(
        f"/api/v1/metric-types/{mt.id}", headers=auth_headers,
    )
    assert response.status_code == 409

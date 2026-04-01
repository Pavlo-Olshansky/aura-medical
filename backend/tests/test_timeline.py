from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel
from app.infrastructure.models.metric_type import MetricTypeModel
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.vaccination import VaccinationModel
from app.infrastructure.models.visit import VisitModel

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


@pytest_asyncio.fixture
async def timeline_data(session: AsyncSession, test_user):
    """Create one record of each type for timeline tests."""
    now = datetime.now(timezone.utc)

    visit = VisitModel(
        user_id=test_user.id,
        date=now - timedelta(days=3),
        doctor="Тестовий лікар",
    )
    session.add(visit)

    treatment = TreatmentModel(
        user_id=test_user.id,
        date_start=now - timedelta(days=2),
        name="Тестове лікування",
        days=10,
        receipt="Тест",
    )
    session.add(treatment)

    lab_result = LabResultModel(
        user_id=test_user.id,
        date=now - timedelta(days=1),
    )
    session.add(lab_result)

    vaccination = VaccinationModel(
        user_id=test_user.id,
        date=now,
        vaccine_name="Тестова вакцина",
        dose_number=1,
    )
    session.add(vaccination)

    await session.commit()
    await session.refresh(visit)
    await session.refresh(treatment)
    await session.refresh(lab_result)
    await session.refresh(vaccination)

    # Add a lab test entry for the lab result
    entry = LabTestEntryModel(
        lab_result_id=lab_result.id,
        biomarker_name="Гемоглобін",
        value=140,
        unit="г/л",
    )
    session.add(entry)
    await session.commit()

    return {
        "visit": visit,
        "treatment": treatment,
        "lab_result": lab_result,
        "vaccination": vaccination,
    }


@pytest.mark.asyncio
async def test_timeline_returns_mixed_events(
    client: AsyncClient, auth_headers: dict, test_user, timeline_data,
):
    response = await client.get("/api/timeline/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4

    # Verify reverse chronological order (newest first)
    event_types = [item["event_type"] for item in data["items"]]
    assert "vaccination" in event_types
    assert "lab_result" in event_types
    assert "treatment" in event_types
    assert "visit" in event_types

    # The most recent event (vaccination) should be first
    assert data["items"][0]["event_type"] == "vaccination"
    # The oldest (visit) should be last
    assert data["items"][3]["event_type"] == "visit"


@pytest.mark.asyncio
async def test_timeline_filter_by_event_type(
    client: AsyncClient, auth_headers: dict, test_user, timeline_data,
):
    response = await client.get(
        "/api/timeline/",
        params={"event_type": "visit"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["event_type"] == "visit"

    response = await client.get(
        "/api/timeline/",
        params={"event_type": "treatment"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["event_type"] == "treatment"


@pytest.mark.asyncio
async def test_timeline_pagination(
    client: AsyncClient, auth_headers: dict, test_user, timeline_data,
):
    response = await client.get(
        "/api/timeline/",
        params={"page": 1, "size": 2},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["pages"] == 2

    # Page 2
    response = await client.get(
        "/api/timeline/",
        params={"page": 2, "size": 2},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_timeline_excludes_deleted(
    client: AsyncClient, auth_headers: dict, test_user, session: AsyncSession,
):
    now = datetime.now(timezone.utc)

    # Create a visit and soft-delete it
    visit = VisitModel(
        user_id=test_user.id,
        date=now,
        doctor="Видалений лікар",
        deleted_at=now,
    )
    session.add(visit)

    # Create a non-deleted visit
    visit_active = VisitModel(
        user_id=test_user.id,
        date=now - timedelta(hours=1),
        doctor="Активний лікар",
    )
    session.add(visit_active)

    # Create a soft-deleted vaccination
    vacc_deleted = VaccinationModel(
        user_id=test_user.id,
        date=now - timedelta(hours=2),
        vaccine_name="Видалена вакцина",
        dose_number=1,
        deleted_at=now,
    )
    session.add(vacc_deleted)

    await session.commit()

    response = await client.get("/api/timeline/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Only the active visit should appear
    assert data["total"] == 1
    assert data["items"][0]["event_type"] == "visit"

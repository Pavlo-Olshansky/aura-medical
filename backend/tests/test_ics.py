from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.domain.entities import KYIV_TZ
from app.infrastructure.models.visit import VisitModel
from app.infrastructure.models.reference import ProcedureModel, ClinicModel, CityModel


@pytest_asyncio.fixture
async def visit_with_refs(session, test_user):
    proc = ProcedureModel(name="УЗД")
    clinic = ClinicModel(name="Клініка Здоров'я")
    city = CityModel(name="Київ")
    session.add_all([proc, clinic, city])
    await session.commit()
    await session.refresh(proc)
    await session.refresh(clinic)
    await session.refresh(city)

    visit = VisitModel(
        user_id=test_user.id,
        date=datetime(2026, 4, 15, 10, 0, tzinfo=KYIV_TZ),
        procedure_id=proc.id,
        clinic_id=clinic.id,
        city_id=city.id,
        doctor="Петренко",
        body_region="chest",
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)
    return visit


@pytest.mark.asyncio
async def test_ics_export_returns_valid_ical(client, auth_headers, visit_with_refs):
    resp = await client.get(
        f"/api/v1/visits/{visit_with_refs.id}/ics",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert "text/calendar" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]

    body = resp.text
    assert "BEGIN:VCALENDAR" in body
    assert "BEGIN:VEVENT" in body
    assert "END:VEVENT" in body
    assert "END:VCALENDAR" in body


@pytest.mark.asyncio
async def test_ics_contains_correct_fields(client, auth_headers, visit_with_refs):
    resp = await client.get(
        f"/api/v1/visits/{visit_with_refs.id}/ics",
        headers=auth_headers,
    )
    body = resp.text
    assert f"visit-{visit_with_refs.id}@medtracker" in body
    assert "УЗД" in body
    assert "Київ" in body


@pytest.mark.asyncio
async def test_ics_requires_auth(client, visit_with_refs):
    resp = await client.get(f"/api/v1/visits/{visit_with_refs.id}/ics")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_ics_not_found(client, auth_headers):
    resp = await client.get("/api/v1/visits/999999/ics", headers=auth_headers)
    assert resp.status_code == 404

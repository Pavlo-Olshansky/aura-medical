from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.domain.entities import KYIV_TZ
from app.infrastructure.models.visit import VisitModel
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.reference import ProcedureModel, ClinicModel, PositionModel, CityModel


@pytest_asyncio.fixture
async def references(session):
    proc = ProcedureModel(name="УЗД")
    clinic = ClinicModel(name="Клініка Здоров'я")
    position = PositionModel(name="Кардіолог")
    city = CityModel(name="Київ")
    session.add_all([proc, clinic, position, city])
    await session.commit()
    await session.refresh(proc)
    await session.refresh(clinic)
    await session.refresh(position)
    await session.refresh(city)
    return {"procedure": proc, "clinic": clinic, "position": position, "city": city}


@pytest_asyncio.fixture
async def sample_visits(session, test_user, references):
    now = datetime.now(KYIV_TZ)
    past_visit = VisitModel(
        user_id=test_user.id,
        date=now - timedelta(days=10),
        procedure_id=references["procedure"].id,
        clinic_id=references["clinic"].id,
        city_id=references["city"].id,
        body_region="chest",
        doctor="Петренко",
    )
    future_visit = VisitModel(
        user_id=test_user.id,
        date=now + timedelta(days=5),
        position_id=references["position"].id,
        clinic_id=references["clinic"].id,
    )
    session.add_all([past_visit, future_visit])
    await session.commit()
    await session.refresh(past_visit)
    await session.refresh(future_visit)
    return [past_visit, future_visit]


@pytest_asyncio.fixture
async def sample_treatment(session, test_user):
    now = datetime.now(KYIV_TZ)
    treatment = TreatmentModel(
        user_id=test_user.id,
        date_start=now - timedelta(days=3),
        name="Амоксицилін",
        days=7,
        receipt="500mg 3 рази на день",
        body_region="throat",
    )
    session.add(treatment)
    await session.commit()
    await session.refresh(treatment)
    return treatment


@pytest.mark.asyncio
async def test_calendar_events_returns_visits_and_treatments(
    client, auth_headers, sample_visits, sample_treatment,
):
    now = datetime.now(KYIV_TZ)
    date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": date_from, "date_to": date_to},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data

    visit_events = [e for e in data["events"] if e["event_type"] == "visit"]
    treatment_events = [e for e in data["events"] if e["event_type"] == "treatment"]
    assert len(visit_events) == 2
    assert len(treatment_events) == 1


@pytest.mark.asyncio
async def test_calendar_events_empty_range(client, auth_headers, sample_visits):
    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": "2020-01-01", "date_to": "2020-01-31"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["events"] == []


@pytest.mark.asyncio
async def test_calendar_visit_label_derivation(
    client, auth_headers, sample_visits, references,
):
    now = datetime.now(KYIV_TZ)
    date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": date_from, "date_to": date_to},
        headers=auth_headers,
    )
    events = resp.json()["events"]
    visit_events = [e for e in events if e["event_type"] == "visit"]

    # Past visit has procedure + clinic
    past = [e for e in visit_events if e["color"] == "#42A5F5"]
    assert len(past) == 1
    assert "УЗД" in past[0]["title"]
    assert "Клініка Здоров'я" in past[0]["title"]

    # Future visit has position + clinic
    future = [e for e in visit_events if e["color"] == "#66BB6A"]
    assert len(future) == 1
    assert "Кардіолог" in future[0]["title"]


@pytest.mark.asyncio
async def test_calendar_visit_has_end_time(client, auth_headers, sample_visits):
    now = datetime.now(KYIV_TZ)
    date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": date_from, "date_to": date_to},
        headers=auth_headers,
    )
    visit_events = [e for e in resp.json()["events"] if e["event_type"] == "visit"]
    for ve in visit_events:
        assert ve["end"] is not None
        assert ve["all_day"] is False


@pytest.mark.asyncio
async def test_calendar_treatment_is_all_day_range(client, auth_headers, sample_treatment):
    now = datetime.now(KYIV_TZ)
    date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    date_to = (now + timedelta(days=30)).strftime("%Y-%m-%d")

    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": date_from, "date_to": date_to},
        headers=auth_headers,
    )
    treatments = [e for e in resp.json()["events"] if e["event_type"] == "treatment"]
    assert len(treatments) == 1
    assert treatments[0]["all_day"] is True
    assert treatments[0]["title"] == "Амоксицилін"
    assert treatments[0]["color"] == "#FFA726"


@pytest.mark.asyncio
async def test_calendar_requires_auth(client):
    resp = await client.get(
        "/api/v1/calendar/events",
        params={"date_from": "2026-04-01", "date_to": "2026-04-30"},
    )
    assert resp.status_code == 403 or resp.status_code == 401


@pytest.mark.asyncio
async def test_calendar_user_ownership(client, auth_headers, session, sample_visits):
    """Other user's visits should not appear."""
    import bcrypt
    from app.infrastructure.models.user import UserModel

    pw_hash = bcrypt.hashpw(b"other", bcrypt.gensalt(rounds=4)).decode()
    other = UserModel(username="other", password_hash=pw_hash, is_active=True)
    session.add(other)
    await session.commit()
    await session.refresh(other)

    other_visit = VisitModel(
        user_id=other.id,
        date=datetime.now(KYIV_TZ),
    )
    session.add(other_visit)
    await session.commit()

    now = datetime.now(KYIV_TZ)
    resp = await client.get(
        "/api/v1/calendar/events",
        params={
            "date_from": (now - timedelta(days=30)).strftime("%Y-%m-%d"),
            "date_to": (now + timedelta(days=30)).strftime("%Y-%m-%d"),
        },
        headers=auth_headers,
    )
    event_ids = [e["id"] for e in resp.json()["events"] if e["event_type"] == "visit"]
    assert other_visit.id not in event_ids


@pytest.mark.asyncio
async def test_future_visit_triggers_reminders(session, test_user):
    """US3: Verify notification service returns reminders for future visits."""
    from app.application.notification_service import NotificationAppService

    now = datetime.now(KYIV_TZ)
    # Visit 6 hours from now — should trigger day_before reminder
    future_visit = VisitModel(
        user_id=test_user.id,
        date=now + timedelta(hours=6),
    )
    session.add(future_visit)
    await session.commit()
    await session.refresh(future_visit)

    svc = NotificationAppService(session)
    reminders = await svc.get_reminders(test_user.id)

    visit_reminders = [r for r in reminders if r["entity_type"] == "visit" and r["entity_id"] == future_visit.id]
    assert len(visit_reminders) >= 1
    reminder_types = {r["reminder_type"] for r in visit_reminders}
    assert "day_before" in reminder_types

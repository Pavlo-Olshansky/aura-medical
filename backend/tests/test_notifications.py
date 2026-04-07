from datetime import datetime, timedelta

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


@pytest.mark.asyncio
async def test_no_reminders_when_empty(client, auth_headers):
    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_visit_reminder_within_24h(client, auth_headers, session, test_user):
    from app.infrastructure.models.visit import VisitModel

    future_date = datetime.now(KYIV_TZ) + timedelta(hours=12)
    visit = VisitModel(user_id=test_user.id, date=future_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    types = {r["reminder_type"] for r in data["items"] if r["entity_type"] == "visit"}
    assert "day_before" in types
    assert "hour_before" not in types  # 12h away, not within 1h


@pytest.mark.asyncio
async def test_visit_reminder_within_1h(client, auth_headers, session, test_user):
    from app.infrastructure.models.visit import VisitModel

    future_date = datetime.now(KYIV_TZ) + timedelta(minutes=30)
    visit = VisitModel(user_id=test_user.id, date=future_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()

    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    data = resp.json()
    types = {r["reminder_type"] for r in data["items"] if r["entity_type"] == "visit"}
    assert "day_before" in types
    assert "hour_before" in types  # 30min away, within both windows


@pytest.mark.asyncio
async def test_no_reminder_for_past_visit(client, auth_headers, session, test_user):
    from app.infrastructure.models.visit import VisitModel

    past_date = datetime.now(KYIV_TZ) - timedelta(hours=1)
    visit = VisitModel(user_id=test_user.id, date=past_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()

    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    data = resp.json()
    visit_reminders = [r for r in data["items"] if r["entity_type"] == "visit"]
    assert len(visit_reminders) == 0


@pytest.mark.asyncio
async def test_treatment_reminder(client, auth_headers, session, test_user):
    from app.infrastructure.models.treatment import TreatmentModel

    future_date = datetime.now(KYIV_TZ) + timedelta(hours=6)
    treatment = TreatmentModel(
        user_id=test_user.id, date_start=future_date, name="Тест", days=7, receipt="1 таблетка"
    )
    session.add(treatment)
    await session.commit()

    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    data = resp.json()
    treatment_reminders = [r for r in data["items"] if r["entity_type"] == "treatment"]
    assert len(treatment_reminders) >= 1
    assert treatment_reminders[0]["title"] == "Лікування: Тест"


@pytest.mark.asyncio
async def test_vaccination_reminder(client, auth_headers, session, test_user):
    from app.infrastructure.models.vaccination import VaccinationModel

    future_date = datetime.now(KYIV_TZ) + timedelta(hours=3)
    vacc = VaccinationModel(
        user_id=test_user.id,
        date=datetime.now(KYIV_TZ),
        vaccine_name="COVID-19",
        next_due_date=future_date,
    )
    session.add(vacc)
    await session.commit()

    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    data = resp.json()
    vacc_reminders = [r for r in data["items"] if r["entity_type"] == "vaccination"]
    assert len(vacc_reminders) >= 1
    assert "COVID-19" in vacc_reminders[0]["title"]


@pytest.mark.asyncio
async def test_dismiss_reminder(client, auth_headers, session, test_user):
    from app.infrastructure.models.visit import VisitModel

    future_date = datetime.now(KYIV_TZ) + timedelta(hours=6)
    visit = VisitModel(user_id=test_user.id, date=future_date, doctor="Тестовий")
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    # Verify reminder exists
    resp = await client.get("/api/v1/notifications/", headers=auth_headers)
    assert resp.json()["count"] >= 1

    # Dismiss it
    dismiss_resp = await client.post(
        "/api/v1/notifications/dismiss",
        json={"entity_type": "visit", "entity_id": visit.id, "reminder_type": "day_before"},
        headers=auth_headers,
    )
    assert dismiss_resp.status_code == 204

    # Verify dismissed
    resp2 = await client.get("/api/v1/notifications/", headers=auth_headers)
    day_reminders = [
        r for r in resp2.json()["items"]
        if r["entity_type"] == "visit" and r["entity_id"] == visit.id and r["reminder_type"] == "day_before"
    ]
    assert len(day_reminders) == 0


@pytest.mark.asyncio
async def test_dismiss_idempotent(client, auth_headers, session, test_user):
    """Dismissing the same reminder twice should not error."""
    resp = await client.post(
        "/api/v1/notifications/dismiss",
        json={"entity_type": "visit", "entity_id": 9999, "reminder_type": "day_before"},
        headers=auth_headers,
    )
    assert resp.status_code == 204

    resp2 = await client.post(
        "/api/v1/notifications/dismiss",
        json={"entity_type": "visit", "entity_id": 9999, "reminder_type": "day_before"},
        headers=auth_headers,
    )
    assert resp2.status_code == 204

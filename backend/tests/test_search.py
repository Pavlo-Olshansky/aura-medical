from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel
from app.infrastructure.models.reference import CityModel, ClinicModel, PositionModel, ProcedureModel
from app.infrastructure.models.treatment import TreatmentModel
from app.infrastructure.models.vaccination import VaccinationModel
from app.infrastructure.models.visit import VisitModel

KYIV = timezone(timedelta(hours=3))


@pytest_asyncio.fixture
async def search_data(session: AsyncSession, test_user):
    position = PositionModel(name="Кардіолог")
    procedure = ProcedureModel(name="ЕКГ")
    clinic = ClinicModel(name="Медком")
    city = CityModel(name="Київ")
    session.add_all([position, procedure, clinic, city])
    await session.flush()

    visit = VisitModel(
        user_id=test_user.id,
        date=datetime(2026, 3, 15, tzinfo=KYIV),
        doctor="Іванов О.П.",
        position_id=position.id,
        procedure_id=procedure.id,
        clinic_id=clinic.id,
        city_id=city.id,
        comment="Профілактичний огляд серця",
        body_region="серце",
    )
    treatment = TreatmentModel(
        user_id=test_user.id,
        date_start=datetime(2026, 3, 1, tzinfo=KYIV),
        name="Аторвастатин",
        days=90,
        receipt="По 1 таблетці вранці",
        body_region=None,
    )
    vaccination = VaccinationModel(
        user_id=test_user.id,
        date=datetime(2026, 2, 10, tzinfo=KYIV),
        vaccine_name="Pfizer COVID-19",
        dose_number=3,
        manufacturer="Pfizer-BioNTech",
    )
    lab_result = LabResultModel(
        user_id=test_user.id,
        date=datetime(2026, 2, 20, tzinfo=KYIV),
        notes="Загальний аналіз крові",
    )
    session.add_all([visit, treatment, vaccination, lab_result])
    await session.flush()

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
        "vaccination": vaccination,
        "lab_result": lab_result,
    }


@pytest.mark.asyncio
async def test_search_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/search/", params={"q": "test"})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_search_rejects_short_query(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/search/", params={"q": "a"}, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_rejects_missing_query(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/search/", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_visits_by_doctor(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "Іванов"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["visits"]["total"] == 1
    assert data["visits"]["items"][0]["doctor"] == "Іванов О.П."


@pytest.mark.asyncio
async def test_search_visits_by_clinic(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "Медком"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["visits"]["total"] == 1
    assert data["visits"]["items"][0]["clinic_name"] == "Медком"


@pytest.mark.asyncio
async def test_search_treatments_by_name(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "Аторва"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["treatments"]["total"] == 1
    assert data["treatments"]["items"][0]["name"] == "Аторвастатин"


@pytest.mark.asyncio
async def test_search_lab_results_by_biomarker(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "Гемоглобін"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["lab_results"]["total"] == 1
    assert "Гемоглобін" in data["lab_results"]["items"][0]["biomarker_names"]


@pytest.mark.asyncio
async def test_search_vaccinations_by_name(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "Pfizer"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["vaccinations"]["total"] == 1
    assert data["vaccinations"]["items"][0]["vaccine_name"] == "Pfizer COVID-19"


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient, auth_headers: dict, search_data):
    response = await client.get("/api/v1/search/", params={"q": "неіснуюче"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["visits"]["total"] == 0
    assert data["treatments"]["total"] == 0
    assert data["lab_results"]["total"] == 0
    assert data["vaccinations"]["total"] == 0


@pytest.mark.asyncio
async def test_search_respects_limit(client: AsyncClient, auth_headers: dict, search_data, session, test_user):
    for i in range(10):
        session.add(VaccinationModel(
            user_id=test_user.id,
            date=datetime(2026, 1, i + 1, tzinfo=KYIV),
            vaccine_name=f"Pfizer dose {i}",
            dose_number=1,
        ))
    await session.commit()

    response = await client.get("/api/v1/search/", params={"q": "Pfizer", "limit": 3}, headers=auth_headers)
    data = response.json()
    assert len(data["vaccinations"]["items"]) == 3
    assert data["vaccinations"]["total"] == 11


@pytest.mark.asyncio
async def test_search_excludes_soft_deleted(client: AsyncClient, auth_headers: dict, search_data, session):
    visit = search_data["visit"]
    visit.deleted_at = datetime.now(KYIV)
    await session.commit()

    response = await client.get("/api/v1/search/", params={"q": "Іванов"}, headers=auth_headers)
    data = response.json()
    assert data["visits"]["total"] == 0


@pytest.mark.asyncio
async def test_search_user_isolation(client: AsyncClient, auth_headers: dict, session):
    from app.infrastructure.models.user import UserModel
    import bcrypt
    pw = bcrypt.hashpw(b"pass2", bcrypt.gensalt(rounds=4)).decode()
    other = UserModel(username="other", password_hash=pw, is_active=True)
    session.add(other)
    await session.flush()

    session.add(VisitModel(
        user_id=other.id,
        date=datetime(2026, 3, 1, tzinfo=KYIV),
        doctor="Секретний Лікар",
    ))
    await session.commit()

    response = await client.get("/api/v1/search/", params={"q": "Секретний"}, headers=auth_headers)
    data = response.json()
    assert data["visits"]["total"] == 0


@pytest.mark.asyncio
async def test_search_case_insensitive_cyrillic(client: AsyncClient, auth_headers: dict, session, test_user):
    """Searching lowercase 'біш' must find uppercase clinic 'БІШ'."""
    clinic = ClinicModel(name="БІШ")
    session.add(clinic)
    await session.flush()
    session.add(VisitModel(
        user_id=test_user.id,
        date=datetime(2026, 4, 1, tzinfo=KYIV),
        clinic_id=clinic.id,
        doctor="Тест",
    ))
    await session.commit()

    response = await client.get("/api/v1/search/", params={"q": "біш"}, headers=auth_headers)
    data = response.json()
    assert data["visits"]["total"] == 1
    assert data["visits"]["items"][0]["clinic_name"] == "БІШ"

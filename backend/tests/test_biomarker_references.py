from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.biomarker_reference import BiomarkerReferenceModel
from app.infrastructure.models.lab_result import LabResultModel, LabTestEntryModel
from app.infrastructure.models.visit import VisitModel


SEED_BIOMARKERS = [
    {"name": "Гемоглобін", "abbreviation": "Hb", "unit": "г/л", "category": "cbc",
     "ref_min": 120, "ref_max": 160, "sort_order": 1},
    {"name": "Еритроцити", "abbreviation": "RBC", "unit": "×10¹²/л", "category": "cbc",
     "ref_min": 3.5, "ref_max": 5.5, "sort_order": 2},
    {"name": "Лейкоцити", "abbreviation": "WBC", "unit": "×10⁹/л", "category": "cbc",
     "ref_min": 4.0, "ref_max": 9.0, "sort_order": 3},
    {"name": "Тромбоцити", "abbreviation": "PLT", "unit": "×10⁹/л", "category": "cbc",
     "ref_min": 150, "ref_max": 400, "sort_order": 4},
    {"name": "Гематокрит", "abbreviation": "Hct", "unit": "%", "category": "cbc",
     "ref_min": 35, "ref_max": 49, "sort_order": 5},
    {"name": "ШОЕ", "abbreviation": "ESR", "unit": "мм/год", "category": "cbc",
     "ref_min": 2, "ref_max": 15, "sort_order": 6},
    {"name": "Глюкоза", "abbreviation": "Glu", "unit": "ммоль/л", "category": "biochemistry",
     "ref_min": 3.9, "ref_max": 5.5, "sort_order": 10},
    {"name": "Загальний холестерин", "abbreviation": "TC", "unit": "ммоль/л", "category": "biochemistry",
     "ref_max": 5.2, "sort_order": 11},
    {"name": "Холестерин ЛПВЩ", "abbreviation": "HDL", "unit": "ммоль/л", "category": "biochemistry",
     "ref_min": 1.0, "ref_max": 2.2, "sort_order": 12},
    {"name": "Холестерин ЛПНЩ", "abbreviation": "LDL", "unit": "ммоль/л", "category": "biochemistry",
     "ref_max": 3.3, "sort_order": 13},
    {"name": "Тригліцериди", "abbreviation": "TG", "unit": "ммоль/л", "category": "biochemistry",
     "ref_max": 1.7, "sort_order": 14},
    {"name": "Креатинін", "abbreviation": "Crea", "unit": "мкмоль/л", "category": "biochemistry",
     "ref_min": 44, "ref_max": 106, "sort_order": 15},
    {"name": "Сечовина", "abbreviation": "Urea", "unit": "ммоль/л", "category": "biochemistry",
     "ref_min": 2.5, "ref_max": 8.3, "sort_order": 16},
    {"name": "АЛТ", "abbreviation": "ALT", "unit": "Од/л", "category": "biochemistry",
     "ref_max": 41, "sort_order": 17},
    {"name": "АСТ", "abbreviation": "AST", "unit": "Од/л", "category": "biochemistry",
     "ref_max": 40, "sort_order": 18},
    {"name": "Білірубін загальний", "abbreviation": "TBIL", "unit": "мкмоль/л", "category": "biochemistry",
     "ref_min": 3.4, "ref_max": 20.5, "sort_order": 19},
    {"name": "Загальний білок", "abbreviation": "TP", "unit": "г/л", "category": "biochemistry",
     "ref_min": 64, "ref_max": 83, "sort_order": 20},
    {"name": "Альбумін", "abbreviation": "ALB", "unit": "г/л", "category": "biochemistry",
     "ref_min": 35, "ref_max": 52, "sort_order": 21},
    {"name": "Сечова кислота", "abbreviation": "UA", "unit": "мкмоль/л", "category": "biochemistry",
     "ref_min": 143, "ref_max": 416, "sort_order": 22},
    {"name": "Залізо сироваткове", "abbreviation": "Fe", "unit": "мкмоль/л", "category": "biochemistry",
     "ref_min": 9.0, "ref_max": 31.3, "sort_order": 23},
    {"name": "Феритин", "abbreviation": "Ferr", "unit": "нг/мл", "category": "biochemistry",
     "ref_min": 10, "ref_max": 250, "sort_order": 24},
    {"name": "С-реактивний білок", "abbreviation": "CRP", "unit": "мг/л", "category": "biochemistry",
     "ref_max": 5.0, "sort_order": 25},
    {"name": "Глікований гемоглобін", "abbreviation": "HbA1c", "unit": "%", "category": "biochemistry",
     "ref_min": 4.0, "ref_max": 5.6, "sort_order": 26},
    {"name": "ТТГ", "abbreviation": "TSH", "unit": "мМО/л", "category": "thyroid",
     "ref_min": 0.27, "ref_max": 4.2, "sort_order": 30},
    {"name": "Вільний Т4", "abbreviation": "FT4", "unit": "пмоль/л", "category": "thyroid",
     "ref_min": 12.0, "ref_max": 22.0, "sort_order": 31},
    {"name": "Вільний Т3", "abbreviation": "FT3", "unit": "пмоль/л", "category": "thyroid",
     "ref_min": 3.1, "ref_max": 6.8, "sort_order": 32},
    {"name": "Вітамін D (25-OH)", "abbreviation": "25-OH-D", "unit": "нг/мл", "category": "vitamins",
     "ref_min": 30, "ref_max": 100, "sort_order": 40},
    {"name": "Вітамін B12", "abbreviation": "B12", "unit": "пг/мл", "category": "vitamins",
     "ref_min": 197, "ref_max": 771, "sort_order": 41},
]


@pytest_asyncio.fixture
async def seed_biomarkers(session: AsyncSession):
    """Insert 28 seed biomarker references matching production seed data."""
    for data in SEED_BIOMARKERS:
        obj = BiomarkerReferenceModel(**data)
        session.add(obj)
    await session.commit()


@pytest.mark.asyncio
async def test_list_biomarker_references(
    client: AsyncClient, auth_headers: dict, seed_biomarkers,
):
    response = await client.get("/api/v1/biomarker-references/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 28


@pytest.mark.asyncio
async def test_create_biomarker_reference(
    client: AsyncClient, auth_headers: dict,
):
    response = await client.post(
        "/api/v1/biomarker-references/",
        json={
            "name": "Інсулін",
            "abbreviation": "INS",
            "unit": "мкМО/мл",
            "category": "biochemistry",
            "ref_min": "2.6",
            "ref_max": "24.9",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Інсулін"
    assert data["abbreviation"] == "INS"
    assert data["unit"] == "мкМО/мл"
    assert data["category"] == "biochemistry"
    assert "id" in data
    assert "created" in data
    assert "updated" in data


@pytest.mark.asyncio
async def test_update_biomarker_reference(
    client: AsyncClient, auth_headers: dict, session: AsyncSession,
):
    obj = BiomarkerReferenceModel(
        name="Тестовий маркер", unit="мг/л", category="cbc", sort_order=0,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    response = await client.put(
        f"/api/v1/biomarker-references/{obj.id}",
        json={"name": "Оновлений маркер", "unit": "г/л"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Оновлений маркер"
    assert data["unit"] == "г/л"
    assert data["id"] == obj.id


@pytest.mark.asyncio
async def test_delete_biomarker_reference(
    client: AsyncClient, auth_headers: dict, session: AsyncSession,
):
    obj = BiomarkerReferenceModel(
        name="Для видалення", unit="мг/л", category="cbc", sort_order=0,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)

    response = await client.delete(
        f"/api/v1/biomarker-references/{obj.id}", headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify deleted
    response = await client.get("/api/v1/biomarker-references/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_search_biomarker_references(
    client: AsyncClient, auth_headers: dict, seed_biomarkers,
):
    response = await client.get(
        "/api/v1/biomarker-references/",
        params={"search": "Глюк"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    names = [item["name"] for item in data]
    assert any("Глюкоз" in n for n in names)


@pytest.mark.asyncio
async def test_delete_in_use_returns_409(
    client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user,
):
    # Create a biomarker reference
    biomarker = BiomarkerReferenceModel(
        name="Маркер у використанні", unit="мг/л", category="cbc", sort_order=0,
    )
    session.add(biomarker)
    await session.commit()
    await session.refresh(biomarker)

    # Create a visit (needed for lab result)
    visit = VisitModel(
        user_id=test_user.id,
        date=datetime.now(timezone.utc),
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)

    # Create a lab result with an entry referencing the biomarker
    lab_result = LabResultModel(
        user_id=test_user.id,
        date=datetime.now(timezone.utc),
        visit_id=visit.id,
    )
    session.add(lab_result)
    await session.commit()
    await session.refresh(lab_result)

    entry = LabTestEntryModel(
        lab_result_id=lab_result.id,
        biomarker_id=biomarker.id,
        biomarker_name="Маркер у використанні",
        value=5.0,
        unit="мг/л",
    )
    session.add(entry)
    await session.commit()

    # Try to delete — should fail with 409
    response = await client.delete(
        f"/api/v1/biomarker-references/{biomarker.id}", headers=auth_headers,
    )
    assert response.status_code == 409

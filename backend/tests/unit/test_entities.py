from datetime import datetime, timedelta

from app.domain.entities import KYIV_TZ, Treatment, Visit


def test_treatment_status_active():
    t = Treatment(user_id=1, date_start=datetime.now(KYIV_TZ), name="Test", days=30, receipt="1/day")
    assert t.status == "active"


def test_treatment_status_completed():
    t = Treatment(user_id=1, date_start=datetime.now(KYIV_TZ) - timedelta(days=60), name="Test", days=30, receipt="1/day")
    assert t.status == "completed"


def test_treatment_end_date():
    start = datetime(2026, 1, 1, tzinfo=KYIV_TZ)
    t = Treatment(user_id=1, date_start=start, name="Test", days=10, receipt="1/day")
    assert t.end_date == start + timedelta(days=10)


def test_visit_soft_delete():
    v = Visit(user_id=1, date=datetime.now(KYIV_TZ))
    assert v.deleted_at is None
    assert not v.is_deleted
    v.soft_delete()
    assert v.deleted_at is not None
    assert v.is_deleted


def test_visit_has_document():
    v = Visit(user_id=1, date=datetime.now(KYIV_TZ))
    assert not v.has_document
    v.attach_document("documents/2026_КТ/scan.pdf")
    assert v.has_document
    assert v.document == "documents/2026_КТ/scan.pdf"


def test_visit_set_body_region_valid():
    v = Visit(user_id=1, date=datetime.now(KYIV_TZ))
    v.set_body_region("chest")
    assert v.body_region == "chest"


def test_visit_set_body_region_none():
    v = Visit(user_id=1, date=datetime.now(KYIV_TZ), body_region="chest")
    v.set_body_region(None)
    assert v.body_region is None


def test_visit_set_body_region_invalid():
    v = Visit(user_id=1, date=datetime.now(KYIV_TZ))
    try:
        v.set_body_region("invalid_region")
        assert False, "Should have raised"
    except Exception as e:
        assert "Invalid body region" in str(e)


def test_treatment_soft_delete():
    t = Treatment(user_id=1, date_start=datetime.now(KYIV_TZ), name="X", days=1, receipt="x")
    t.soft_delete()
    assert t.is_deleted

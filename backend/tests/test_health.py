import pytest


@pytest.mark.asyncio
async def test_health_liveness(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)


@pytest.mark.asyncio
async def test_health_readiness_ok(client):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["weather_service"] in ("ok", "unavailable")


@pytest.mark.asyncio
async def test_health_readiness_weather_unavailable(client):
    """Weather being unavailable should not cause 503."""
    from app.main import app

    original = getattr(app.state, "skypulse", None)
    app.state.skypulse = None
    try:
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["checks"]["weather_service"] == "unavailable"
    finally:
        app.state.skypulse = original

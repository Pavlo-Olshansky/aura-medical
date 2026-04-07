import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.infrastructure.database import async_session

router = APIRouter()


@router.get("/health")
async def liveness(request: Request):
    started_at = getattr(request.app.state, "started_at", None)
    uptime = round(time.time() - started_at) if started_at else 0
    return {
        "status": "ok",
        "version": request.app.version,
        "uptime_seconds": uptime,
    }


@router.get("/health/ready")
async def readiness(request: Request):
    checks: dict[str, str] = {}

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    skypulse = getattr(request.app.state, "skypulse", None)
    checks["weather_service"] = "ok" if skypulse is not None else "unavailable"

    status = "ok" if checks["database"] == "ok" else "unavailable"
    status_code = 200 if status == "ok" else 503

    return JSONResponse(
        status_code=status_code,
        content={"status": status, "checks": checks},
    )

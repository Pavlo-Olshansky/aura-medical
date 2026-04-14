import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.config import settings
from app.domain.exceptions import AuthenticationError, DomainError, EntityNotFound, ReferenceInUse
from app.infrastructure.database import engine
from app.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.logging import setup_logging
    setup_logging()

    skypulse_client = None
    try:
        from skypulse import AsyncSkyPulseClient, CacheConfig, Units
        skypulse_client = AsyncSkyPulseClient(
            api_key=settings.SKYPULSE_API_KEY or None,
            units=Units.METRIC,
            language="uk",
            cache=CacheConfig(enabled=True, ttl=300, max_entries=64),
        )
    except Exception:
        pass
    app.state.skypulse = skypulse_client
    app.state.started_at = time.time()

    from app.infrastructure.scheduler import init_scheduler, shutdown_scheduler
    init_scheduler()

    yield

    shutdown_scheduler()
    if skypulse_client:
        await skypulse_client.close()
    await engine.dispose()


app = FastAPI(
    title="MedTracker API",
    description="Personal medical records tracker",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(EntityNotFound)
async def entity_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(ReferenceInUse)
async def reference_in_use_handler(request, exc):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def domain_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


from app.api.health import router as health_router

app.include_router(health_router)
app.include_router(api_router)

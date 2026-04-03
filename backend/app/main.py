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
    yield
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
    allow_methods=["*"],
    allow_headers=["*"],
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


app.include_router(api_router)

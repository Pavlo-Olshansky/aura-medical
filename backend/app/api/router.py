from fastapi import APIRouter

from app.api import auth, visits, treatments, references, dashboard, profile

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(treatments.router, prefix="/treatments", tags=["treatments"])
api_router.include_router(references.positions_router, prefix="/positions", tags=["references"])
api_router.include_router(references.procedures_router, prefix="/procedures", tags=["references"])
api_router.include_router(references.clinics_router, prefix="/clinics", tags=["references"])
api_router.include_router(references.cities_router, prefix="/cities", tags=["references"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])

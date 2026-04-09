from fastapi import APIRouter

from app.api import (
    auth, visits, treatments, references, dashboard, profile,
    biomarker_references, metric_types, lab_results, health_metrics,
    vaccinations, timeline, weather, notifications, push, calendar,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(treatments.router, prefix="/treatments", tags=["treatments"])
api_router.include_router(references.positions_router, prefix="/positions", tags=["references"])
api_router.include_router(references.procedures_router, prefix="/procedures", tags=["references"])
api_router.include_router(references.clinics_router, prefix="/clinics", tags=["references"])
api_router.include_router(references.cities_router, prefix="/cities", tags=["references"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(biomarker_references.router, prefix="/biomarker-references", tags=["biomarker-references"])
api_router.include_router(metric_types.router, prefix="/metric-types", tags=["metric-types"])
api_router.include_router(lab_results.router, prefix="/lab-results", tags=["lab-results"])
api_router.include_router(health_metrics.router, prefix="/health-metrics", tags=["health-metrics"])
api_router.include_router(vaccinations.router, prefix="/vaccinations", tags=["vaccinations"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(push.router, prefix="/push", tags=["push"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])

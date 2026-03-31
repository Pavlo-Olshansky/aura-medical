from __future__ import annotations

from app.domain.repositories import TreatmentRepository, VisitRepository


class DashboardAppService:
    def __init__(self, visit_repo: VisitRepository, treatment_repo: TreatmentRepository):
        self._visit_repo = visit_repo
        self._treatment_repo = treatment_repo

    async def get_dashboard(self, user_id: int) -> dict:
        recent_visits = await self._visit_repo.list_recent(user_id, limit=10)
        total_visits = await self._visit_repo.count_total(user_id)

        all_treatments = await self._treatment_repo.list_all(user_id)
        active = [t for t in all_treatments if t.status == "active"]

        treatment_regions = list({
            t.body_region for t in active
            if t.body_region and t.body_region != "whole_body"
        })

        return {
            "recent_visits": recent_visits,
            "total_visits": total_visits,
            "all_treatments": all_treatments,
            "active_treatments": active,
            "treatment_regions": treatment_regions,
        }

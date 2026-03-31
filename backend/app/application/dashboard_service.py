from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

from app.domain.entities import KYIV_TZ, Treatment, Visit
from app.domain.repositories import TreatmentRepository, VisitRepository
from app.domain.value_objects import BODY_REGION_LABELS
from app.schemas.body_map import (
    BodyMapSummaryResponse,
    BodyMapTreatmentItem,
    BodyMapVisitItem,
    BodyRegionDetailResponse,
    BodyRegionSummary,
)


class DashboardAppService:
    def __init__(self, visit_repo: VisitRepository, treatment_repo: TreatmentRepository):
        self._visit_repo = visit_repo
        self._treatment_repo = treatment_repo

    async def get_dashboard(self, user_id: int) -> dict:
        recent_visits = await self._visit_repo.list_recent(user_id, limit=10)
        total_visits = await self._visit_repo.count_total(user_id)

        all_treatments = await self._treatment_repo.list_all(user_id)
        active = [t for t in all_treatments if t.status == "active"]

        return {
            "recent_visits": recent_visits,
            "total_visits": total_visits,
            "all_treatments": all_treatments,
            "active_treatments": active,
        }

    async def get_body_map_summary(self, user_id: int) -> BodyMapSummaryResponse:
        visit_rows = await self._visit_repo.count_by_region(user_id)
        all_treatments = await self._treatment_repo.list_all(user_id)

        active_by_region: dict[str, int] = {}
        for t in all_treatments:
            if t.status == "active" and t.body_region and t.body_region != "whole_body":
                active_by_region[t.body_region] = active_by_region.get(t.body_region, 0) + 1

        regions: dict[str, BodyRegionSummary] = {}
        for row in visit_rows:
            key = row["body_region"]
            if key == "whole_body":
                continue
            regions[key] = BodyRegionSummary(
                visit_count=row["visit_count"],
                active_treatment_count=active_by_region.pop(key, 0),
                last_visit_date=row["last_visit_date"],
                visits_last_year=row["visits_last_year"],
            )

        for key, count in active_by_region.items():
            if key not in regions:
                regions[key] = BodyRegionSummary(
                    visit_count=0, active_treatment_count=count,
                    last_visit_date=None, visits_last_year=0,
                )

        unmapped = await self._visit_repo.count_unmapped(user_id)
        whole_body = await self._visit_repo.count_whole_body(user_id)

        return BodyMapSummaryResponse(
            regions=regions,
            unmapped_visit_count=unmapped,
            whole_body_visit_count=whole_body,
        )

    async def get_body_map_detail(self, user_id: int, region_key: str, limit: int = 20, offset: int = 0) -> BodyRegionDetailResponse:
        label = BODY_REGION_LABELS.get(region_key, region_key)

        visits = await self._visit_repo.list_by_region(user_id, region_key, limit, offset)
        treatments = await self._treatment_repo.list_by_region(user_id, region_key)

        visit_items = [
            BodyMapVisitItem(
                id=v.id, date=v.date, doctor=v.doctor,
                position_name=v.position.name if v.position else None,
                procedure_name=v.procedure.name if v.procedure else None,
                clinic_name=v.clinic.name if v.clinic else None,
                has_document=v.has_document,
            )
            for v in visits
        ]

        treatment_items = [
            BodyMapTreatmentItem(
                id=t.id, name=t.name, date_start=t.date_start,
                days=t.days, date_end=t.end_date, status=t.status,
            )
            for t in treatments
        ]

        return BodyRegionDetailResponse(
            region=region_key, label=label,
            visits=visit_items, treatments=treatment_items,
        )

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants.body_regions import BODY_REGION_LABELS, BODY_REGION_VALUES
from app.models.treatment import Treatment, KYIV_TZ
from app.models.visit import Visit
from app.schemas.body_map import (
    BodyMapSummaryResponse,
    BodyMapTreatmentItem,
    BodyMapVisitItem,
    BodyRegionDetailResponse,
    BodyRegionSummary,
)
from app.services.treatment import compute_status


async def get_body_map_summary(user_id: int, session: AsyncSession) -> BodyMapSummaryResponse:
    now = datetime.now(KYIV_TZ)
    one_year_ago = now - timedelta(days=365)

    # Visit aggregation by body_region
    visit_query = (
        select(
            Visit.body_region,
            func.count().label("visit_count"),
            func.count().filter(Visit.date >= one_year_ago).label("visits_last_year"),
            func.max(Visit.date).label("last_visit_date"),
        )
        .where(
            Visit.user_id == user_id,
            Visit.deleted_at.is_(None),
            Visit.body_region.isnot(None),
        )
        .group_by(Visit.body_region)
    )
    visit_result = await session.execute(visit_query)
    visit_rows = visit_result.all()

    # Treatment aggregation — active treatments by body_region
    treatment_query = select(Treatment).where(
        Treatment.user_id == user_id,
        Treatment.deleted_at.is_(None),
        Treatment.body_region.isnot(None),
    )
    treatment_result = await session.execute(treatment_query)
    treatments = treatment_result.scalars().all()

    active_by_region: dict[str, int] = {}
    for t in treatments:
        if compute_status(t.date_start, t.days) == "active":
            active_by_region[t.body_region] = active_by_region.get(t.body_region, 0) + 1

    # Build regions dict
    regions: dict[str, BodyRegionSummary] = {}
    for row in visit_rows:
        region_key = row.body_region
        if region_key == "whole_body":
            continue
        regions[region_key] = BodyRegionSummary(
            visit_count=row.visit_count,
            active_treatment_count=active_by_region.pop(region_key, 0),
            last_visit_date=row.last_visit_date,
            visits_last_year=row.visits_last_year,
        )

    # Add regions that have active treatments but no visits
    for region_key, count in active_by_region.items():
        if region_key == "whole_body":
            continue
        if region_key not in regions:
            regions[region_key] = BodyRegionSummary(
                visit_count=0,
                active_treatment_count=count,
                last_visit_date=None,
                visits_last_year=0,
            )

    # Unmapped and whole_body counts
    unmapped_result = await session.execute(
        select(func.count()).select_from(Visit).where(
            Visit.user_id == user_id,
            Visit.deleted_at.is_(None),
            Visit.body_region.is_(None),
        )
    )
    unmapped_visit_count = unmapped_result.scalar() or 0

    whole_body_result = await session.execute(
        select(func.count()).select_from(Visit).where(
            Visit.user_id == user_id,
            Visit.deleted_at.is_(None),
            Visit.body_region == "whole_body",
        )
    )
    whole_body_visit_count = whole_body_result.scalar() or 0

    return BodyMapSummaryResponse(
        regions=regions,
        unmapped_visit_count=unmapped_visit_count,
        whole_body_visit_count=whole_body_visit_count,
    )


async def get_body_map_detail(
    user_id: int, region_key: str, session: AsyncSession, limit: int = 20, offset: int = 0
) -> BodyRegionDetailResponse:
    label = BODY_REGION_LABELS.get(region_key, region_key)

    # Visits for this region
    visits_query = (
        select(Visit)
        .where(
            Visit.user_id == user_id,
            Visit.deleted_at.is_(None),
            Visit.body_region == region_key,
        )
        .options(
            selectinload(Visit.position),
            selectinload(Visit.procedure),
            selectinload(Visit.clinic),
        )
        .order_by(Visit.date.desc())
        .offset(offset)
        .limit(limit)
    )
    visits_result = await session.execute(visits_query)
    visits = visits_result.scalars().all()

    visit_items = [
        BodyMapVisitItem(
            id=v.id,
            date=v.date,
            doctor=v.doctor,
            position_name=v.position.name if v.position else None,
            procedure_name=v.procedure.name if v.procedure else None,
            clinic_name=v.clinic.name if v.clinic else None,
            has_document=bool(v.document),
        )
        for v in visits
    ]

    # Treatments for this region
    treatments_query = (
        select(Treatment)
        .where(
            Treatment.user_id == user_id,
            Treatment.deleted_at.is_(None),
            Treatment.body_region == region_key,
        )
        .order_by(Treatment.date_start.desc())
    )
    treatments_result = await session.execute(treatments_query)
    treatments = treatments_result.scalars().all()

    treatment_items = [
        BodyMapTreatmentItem(
            id=t.id,
            name=t.name,
            date_start=t.date_start,
            days=t.days,
            date_end=t.date_start + timedelta(days=t.days),
            status=compute_status(t.date_start, t.days),
        )
        for t in treatments
    ]

    return BodyRegionDetailResponse(
        region=region_key,
        label=label,
        visits=visit_items,
        treatments=treatment_items,
    )

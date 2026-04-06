"""
Backfill body_region for existing visits based on doctor specialty.

Only sets body_region for visits where:
1. body_region is currently NULL
2. The visit has a position (doctor specialty)
3. That specialty maps to exactly ONE region in SPECIALTY_REGION_MAP

Usage:
    cd backend && source venv/bin/activate
    python scripts/backfill_body_regions.py [--dry-run]
"""

import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure app modules are importable
sys.path.insert(0, ".")

from app.constants.body_regions import SPECIALTY_REGION_MAP
from app.database import async_session
from app.infrastructure.models.visit import VisitModel


async def backfill(dry_run: bool = False) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(VisitModel)
            .where(VisitModel.body_region.is_(None), VisitModel.deleted_at.is_(None))
            .options()
        )
        visits = result.scalars().all()

        # Preload positions
        from app.infrastructure.models.reference import PositionModel
        pos_result = await session.execute(select(PositionModel))
        positions = {p.id: p.name for p in pos_result.scalars().all()}

        updated = 0
        skipped = 0

        for visit in visits:
            if not visit.position_id:
                skipped += 1
                continue

            position_name = positions.get(visit.position_id)
            if not position_name:
                skipped += 1
                continue

            regions = SPECIALTY_REGION_MAP.get(position_name, [])
            if len(regions) == 1:
                region = regions[0]
                if not dry_run:
                    visit.body_region = region
                updated += 1
                print(f"  Visit {visit.id} ({position_name}) → {region}")
            else:
                skipped += 1

        if not dry_run:
            await session.commit()

        prefix = "[DRY RUN] " if dry_run else ""
        print(f"\n{prefix}Done: {updated} visits updated, {skipped} skipped")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill body_region for visits")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()

    asyncio.run(backfill(dry_run=args.dry_run))


if __name__ == "__main__":
    main()

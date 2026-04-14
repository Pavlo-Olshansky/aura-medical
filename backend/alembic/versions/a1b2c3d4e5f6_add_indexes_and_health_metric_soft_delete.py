"""add compound indexes and health_metric soft delete

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-04-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deleted_at column to health_metric for soft delete
    op.add_column(
        "health_metric",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Compound indexes for soft-delete filtering
    op.create_index("ix_visit_user_deleted_at", "visit", ["user_id", "deleted_at"])
    op.create_index("ix_treatment_user_deleted_at", "treatment", ["user_id", "deleted_at"])
    op.create_index("ix_vaccination_user_deleted_at", "vaccination", ["user_id", "deleted_at"])
    op.create_index("ix_health_metric_user_deleted_at", "health_metric", ["user_id", "deleted_at"])
    op.create_index("ix_lab_result_user_deleted_at", "lab_result", ["user_id", "deleted_at"])

    # Compound indexes for date-filtered list queries (missing ones)
    op.create_index("ix_vaccination_user_date", "vaccination", ["user_id", "date"])
    op.create_index("ix_lab_result_user_date", "lab_result", ["user_id", "date"])


def downgrade() -> None:
    op.drop_index("ix_lab_result_user_date", "lab_result")
    op.drop_index("ix_vaccination_user_date", "vaccination")

    op.drop_index("ix_lab_result_user_deleted_at", "lab_result")
    op.drop_index("ix_health_metric_user_deleted_at", "health_metric")
    op.drop_index("ix_vaccination_user_deleted_at", "vaccination")
    op.drop_index("ix_treatment_user_deleted_at", "treatment")
    op.drop_index("ix_visit_user_deleted_at", "visit")

    op.drop_column("health_metric", "deleted_at")

"""add apscheduler jobs table

Revision ID: f1a2b3c4d5e6
Revises: e9df8a752240
Create Date: 2026-04-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e9df8a752240"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apscheduler_jobs",
        sa.Column("id", sa.Unicode(191), primary_key=True),
        sa.Column("next_run_time", sa.Float(25), index=True),
        sa.Column("job_state", sa.LargeBinary, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("apscheduler_jobs")

"""Drop redundant visit indexes

Revision ID: 52d08cb9b8cd
Revises: f1a2b3c4d5e6
Create Date: 2026-04-09 09:33:53.194421

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '52d08cb9b8cd'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_visit_date'), table_name='visit')
    op.drop_index(op.f('ix_visit_user_id'), table_name='visit')


def downgrade() -> None:
    op.create_index(op.f('ix_visit_user_id'), 'visit', ['user_id'], unique=False)
    op.create_index(op.f('ix_visit_date'), 'visit', ['date'], unique=False)

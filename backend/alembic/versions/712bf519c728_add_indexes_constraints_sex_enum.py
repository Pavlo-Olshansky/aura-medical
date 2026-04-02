"""add indexes, constraints, sex enum

Revision ID: 712bf519c728
Revises: dd4476dae74a
Create Date: 2026-04-02 12:14:27.149218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '712bf519c728'
down_revision: Union[str, Sequence[str], None] = 'dd4476dae74a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_health_metric_user_date', 'health_metric', ['user_id', 'date'], unique=False)
    op.create_index('ix_treatment_user_date_start', 'treatment', ['user_id', 'date_start'], unique=False)
    op.create_check_constraint('ck_treatment_days_positive', 'treatment', 'days >= 1')
    sexenum = sa.Enum('male', 'female', name='sexenum')
    sexenum.create(op.get_bind(), checkfirst=True)
    # Drop old default before type change, then re-add
    op.alter_column('user', 'sex', server_default=None,
               existing_type=sa.VARCHAR(length=10), existing_nullable=False)
    op.alter_column('user', 'sex',
               existing_type=sa.VARCHAR(length=10),
               type_=sexenum,
               existing_nullable=False,
               postgresql_using="sex::sexenum")
    op.alter_column('user', 'sex', server_default=sa.text("'male'"),
               existing_type=sexenum, existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('user', 'sex',
               existing_type=sa.Enum('male', 'female', name='sexenum'),
               type_=sa.VARCHAR(length=10),
               existing_nullable=False,
               existing_server_default=sa.text("'male'::character varying"),
               postgresql_using="sex::text")
    sa.Enum('male', 'female', name='sexenum').drop(op.get_bind(), checkfirst=True)
    op.drop_constraint('ck_treatment_days_positive', 'treatment', type_='check')
    op.drop_index('ix_treatment_user_date_start', table_name='treatment')
    op.drop_index('ix_health_metric_user_date', table_name='health_metric')

"""Add new field in simpleone

Revision ID: e2b5215a22f2
Revises: a5d7c7801a17
Create Date: 2024-10-29 16:41:37.108931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2b5215a22f2'
down_revision: Union[str, None] = 'a5d7c7801a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('simpleones', sa.Column('sla_alert_sending', sa.Boolean()))


def downgrade() -> None:
    op.drop_column('simpleones', 'sla_alert_sending')

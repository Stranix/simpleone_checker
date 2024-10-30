"""Initial tables

Revision ID: a5d7c7801a17
Revises: 
Create Date: 2024-10-25 09:43:15.939964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5d7c7801a17'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('simpleones',
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('number', sa.String(), nullable=False),
    sa.Column('assignment_group', sa.String(), nullable=False),
    sa.Column('attention_required', sa.Boolean(), nullable=False),
    sa.Column('caller_department', sa.String(), nullable=True),
    sa.Column('company', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('opened_at', sa.DateTime(), nullable=False),
    sa.Column('service', sa.String(), nullable=False),
    sa.Column('additional_rem_configuration', sa.String(), nullable=False),
    sa.Column('sla_due', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('sys_id', sa.BigInteger(), nullable=False),
    sa.Column('contact_information', sa.String(), nullable=False),
    sa.Column('max_processing_duration', sa.String(), nullable=True),
    sa.Column('out_of_sla', sa.Boolean(), nullable=False),
    sa.Column('reason_for_waiting', sa.String(), nullable=True),
    sa.Column('reopen_counter', sa.Integer(), nullable=False),
    sa.Column('sla_term', sa.DateTime(), nullable=True),
    sa.Column('wait_untill', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_simpleones')),
    sa.UniqueConstraint('number', name=op.f('uq_simpleones_number')),
    sa.UniqueConstraint('sys_id', name=op.f('uq_simpleones_sys_id'))
    )


def downgrade() -> None:
    op.drop_table('simpleones')

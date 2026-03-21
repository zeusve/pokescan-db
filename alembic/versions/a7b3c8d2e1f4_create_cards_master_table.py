"""create cards_master table

Revision ID: a7b3c8d2e1f4
Revises: c10345f90d5a
Create Date: 2026-03-21 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'a7b3c8d2e1f4'
down_revision: Union[str, None] = 'c10345f90d5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension exists before creating table
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.create_table(
        'cards_master',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('set_id', sa.String(), nullable=False),
        sa.Column('rarity', sa.String(), nullable=True),
        sa.Column('image_hash', Vector(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_cards_master_api_id'), 'cards_master', ['api_id'], unique=True)
    op.create_index(op.f('ix_cards_master_set_id'), 'cards_master', ['set_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cards_master_set_id'), table_name='cards_master')
    op.drop_index(op.f('ix_cards_master_api_id'), table_name='cards_master')
    op.drop_table('cards_master')

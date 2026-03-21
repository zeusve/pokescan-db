"""update card_master vector dimension to match ImageHasher.VECTOR_DIM

Revision ID: b8c4d9e3f2a5
Revises: a7b3c8d2e1f4
Create Date: 2026-03-21 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'b8c4d9e3f2a5'
down_revision: Union[str, None] = 'a7b3c8d2e1f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'cards_master',
        'image_hash',
        type_=Vector(512),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'cards_master',
        'image_hash',
        type_=Vector(64),
        existing_nullable=True,
    )

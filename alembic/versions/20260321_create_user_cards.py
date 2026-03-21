"""create user_cards table

Revision ID: d4e5f6a7b8c9
Revises: b8c4d9e3f2a5
Create Date: 2026-03-21 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'b8c4d9e3f2a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_master_id', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(), nullable=False, server_default='UNKNOWN'),
        sa.Column('location', sa.String(), nullable=False, server_default=''),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['card_master_id'], ['cards_master.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_cards_user_id'), 'user_cards', ['user_id'])
    op.create_index(op.f('ix_user_cards_card_master_id'), 'user_cards', ['card_master_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_user_cards_card_master_id'), table_name='user_cards')
    op.drop_index(op.f('ix_user_cards_user_id'), table_name='user_cards')
    op.drop_table('user_cards')

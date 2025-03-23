"""Add car table

Revision ID: 885e958ea59a
Revises: bbfb5e02c020
Create Date: 2025-03-23 00:31:52.505164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '885e958ea59a'
down_revision: Union[str, None] = 'bbfb5e02c020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cart_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status', sa.Enum('ADDED', 'DELETED', 'ORDERED', name='carstatus'), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['item_table.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cart_table')
    # ### end Alembic commands ###

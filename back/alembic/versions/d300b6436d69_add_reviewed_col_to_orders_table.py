"""Add reviewed col to orders table

Revision ID: d300b6436d69
Revises: 55501c343832
Create Date: 2025-04-03 08:47:39.457428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd300b6436d69'
down_revision: Union[str, None] = '55501c343832'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('order_table', sa.Column('reviewed', sa.Boolean(), nullable=True))
    
    op.execute("UPDATE order_table SET reviewed = false WHERE reviewed IS NULL")
    
    op.alter_column('order_table', 'reviewed', existing_type=sa.Boolean(), nullable=False, server_default=sa.text("false"))

def downgrade() -> None:
    op.drop_column('order_table', 'reviewed')

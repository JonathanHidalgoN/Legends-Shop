"""Make description col more characters

Revision ID: b0b0f75c94a9
Revises: 90195995df01
Create Date: 2025-02-13 07:52:31.395118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0b0f75c94a9'
down_revision: Union[str, None] = '90195995df01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item_table', 'description',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.String(length=800),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item_table', 'description',
               existing_type=sa.String(length=800),
               type_=sa.VARCHAR(length=500),
               existing_nullable=False)
    # ### end Alembic commands ###

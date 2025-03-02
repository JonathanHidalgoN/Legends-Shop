"""Add order table

Revision ID: 0f6b8d54c941
Revises: f8bd7715d860
Create Date: 2025-02-25 14:45:51.120504

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f6b8d54c941"
down_revision: Union[str, None] = "f8bd7715d860"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "order_table",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item_table.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_table.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("order_table")
    # ### end Alembic commands ###

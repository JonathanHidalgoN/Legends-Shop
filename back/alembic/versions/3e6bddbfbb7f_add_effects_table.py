"""Add effects table

Revision ID: 3e6bddbfbb7f
Revises: 17578b5f7883
Create Date: 2025-02-08 17:10:43.875323

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3e6bddbfbb7f"
down_revision: Union[str, None] = "17578b5f7883"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "effects_table",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "item_effect_association",
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("effect_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["effect_id"],
            ["effects_table.id"],
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["item_table.id"],
        ),
        sa.PrimaryKeyConstraint("item_id", "effect_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("item_effect_association")
    op.drop_table("effects_table")
    # ### end Alembic commands ###

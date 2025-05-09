"""Add stats mapping table

Revision ID: 91df02ac02a3
Revises: 3f500d9f7ff8
Create Date: 2025-02-15 11:43:29.371223

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91df02ac02a3"
down_revision: Union[str, None] = "3f500d9f7ff8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "stats_mapping_table",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("mapped_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mapped_name"),
        sa.UniqueConstraint("original_name"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("stats_mapping_table")
    # ### end Alembic commands ###

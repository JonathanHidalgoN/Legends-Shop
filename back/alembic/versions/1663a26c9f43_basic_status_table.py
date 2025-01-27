"""Basic status table

Revision ID: 1663a26c9f43
Revises:
Create Date: 2025-01-26 10:22:55.007069

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1663a26c9f43"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME: str = "Status"


def upgrade():
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer, primary_key=True),
    )


def downgrade():
    op.drop_table(TABLE_NAME)

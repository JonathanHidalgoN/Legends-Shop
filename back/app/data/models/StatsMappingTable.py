from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class StatsMappingTable(base):
    __tablename__ = "stats_mapping_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    original_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    mapped_name: Mapped[str] = mapped_column(unique=True, nullable=False)

from sqlalchemy import Column, Float, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base
from app.data.models.ItemTable import ItemTable

ItemStatAssociation = Table(
    "item_stat_association",
    base.metadata,
    Column("item_id", Integer, ForeignKey("item_table.id"), primary_key=True),
    Column("stat_id", Integer, ForeignKey("stats_table.id"), primary_key=True),
    Column("value", Float, nullable=False),
)


class StatsTable(base):
    __tablename__ = "stats_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary=ItemStatAssociation
    )

    def __repr__(self) -> str:
        return f"<StatsTable(id={self.id}, name={self.name!r})>"

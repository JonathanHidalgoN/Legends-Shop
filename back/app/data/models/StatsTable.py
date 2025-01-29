from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base


class ItemStatAssociation(base):
    __tablename__ = "item_stat_association"
    # This many to many relationship table refers to the other tables with the class
    item_id: Mapped[int] = mapped_column(
        ForeignKey("item_table.id"), primary_key=True, nullable=False
    )
    # name no the table name
    stat_id: Mapped[int] = mapped_column(
        ForeignKey("stats_table.id"), primary_key=True, nullable=False
    )
    stat_value: Mapped[float] = mapped_column(Float, nullable=False)


class StatsTable(base):
    __tablename__ = "stats_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary="ItemStatAssociation", back_populates="stats"
    )

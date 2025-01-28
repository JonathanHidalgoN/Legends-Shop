from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from models.ItemTable import ItemTable


class ItemStatAssociation(declarative_base()):
    __tablename__ = "item_stat_association"
    # This many to many relationship table refers to the other tables with the class
    item_id: Mapped[int] = mapped_column(ForeignKey("ItemTable.id"), primary_key=True)
    # name no the table name
    stat_id: Mapped[int] = mapped_column(ForeignKey("StatsTable.id"), primary_key=True)
    stat_value: Mapped[float] = mapped_column(Float, nullable=False)


class StatsTable(declarative_base()):
    __tablename__ = "stats_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        secondary="ItemStatAssociation", back_populates="stats"
    )

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from models.StatsTable import StatsTable
from models.TagsTable import TagsTable


class ItemTable(declarative_base()):
    __tablename__ = "item_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    plain_text: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String(100), nullable=False)
    items: Mapped[list["StatsTable"]] = relationship(
        secondary="ItemStatAssociation", back_populates="items"
    )
    tags: Mapped[list["TagsTable"]] = relationship(
        secondary="ItemTagAssociation", back_populates="items"
    )
    updated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    gold_id: Mapped[int] = mapped_column(ForeignKey("gold_table.id"), nullable=False)

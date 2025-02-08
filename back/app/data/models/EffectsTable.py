from sqlalchemy import Column, Float, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base
from app.data.models.ItemTable import ItemTable

ItemEffectAssociation = Table(
    "item_effect_association",
    base.metadata,
    Column("item_id", Integer, ForeignKey("item_table.id"), primary_key=True),
    Column("effect_id", Integer, ForeignKey("effects_table.id"), primary_key=True),
    Column("value", Float, nullable=False),
)


class EffectsTable(base):
    __tablename__ = "effects_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary=ItemEffectAssociation
    )

    def __repr__(self) -> str:
        return f"<StatsTable(id={self.id}, name={self.name!r})>"

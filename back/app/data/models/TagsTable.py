from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.models.ItemTable import ItemTable
from sqlalchemy.schema import Table
from app.data.database import base

ItemTagsAssociation = Table(
    "item_tags_association",
    base.metadata,
    Column("item_id", Integer, ForeignKey("item_table.id"), primary_key=True),
    Column("tags_id", Integer, ForeignKey("tags_table.id"), primary_key=True),
)

class TagsTable(base):
    __tablename__ = "tags_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary=ItemTagsAssociation
    )

    def __repr__(self) -> str:
        return f"<TagsTable(id={self.id}, name={self.name!r})>"

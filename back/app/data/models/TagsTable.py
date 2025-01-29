from sqlalchemy import ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base


class ItemTagsAssociation(base):
    __tablename__ = "item_tags_association"
    item_id: Mapped[int] = mapped_column(
        ForeignKey("item_table.id"), primary_key=True, nullable=False
    )
    tags_id: Mapped[int] = mapped_column(
        ForeignKey("tags_table.id"), primary_key=True, nullable=False
    )


class TagsTable(base):
    __tablename__ = "tags_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary="ItemTagsAssociation", back_populates="tags"
    )

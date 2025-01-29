from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base


class ItemTagsAssociation(base):
    __tablename__ = "item_tags_association"
    item_id: Mapped[int] = mapped_column(ForeignKey("item_table.id"), primary_key=True)
    tags_id: Mapped[int] = mapped_column(ForeignKey("tags_table.id"), primary_key=True)


class TagsTable(base):
    __tablename__ = "tags_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable", secondary="ItemTagsAssociation", back_populates="tags"
    )

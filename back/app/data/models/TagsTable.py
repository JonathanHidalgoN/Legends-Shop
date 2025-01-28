from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from models.ItemTable import ItemTable


class ItemTagsAssociation(declarative_base()):
    __tablename__ = "item_tags_association"
    item_id: Mapped[int] = mapped_column(ForeignKey("ItemTable.id"), primary_key=True)
    tags_id: Mapped[int] = mapped_column(ForeignKey("TagsTable.id"), primary_key=True)


class TagsTable(declarative_base()):
    __tablename__ = "tags_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    items: Mapped[list["ItemTable"]] = relationship(
        secondary="ItemTagsAssociation", back_populates="tags"
    )

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class ItemTable(base):
    __tablename__ = "item_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    plain_text: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    image: Mapped[str] = mapped_column(String(100), nullable=False)
    imageUrl: Mapped[str] = mapped_column(String(100), nullable=False)
    imageHDPath: Mapped[str] = mapped_column(String(100), nullable=True)
    updated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    gold_id: Mapped[int] = mapped_column(ForeignKey("gold_table.id"), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ItemTable(id={self.id}, name={self.name!r}, plain_text={self.plain_text!r}, "
            f"image={self.image!r}, imageUrl={self.imageUrl!r}, "
            f"updated={self.updated}, gold_id={self.gold_id})>"
        )

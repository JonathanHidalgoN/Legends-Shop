from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class ItemTable(base):
    __tablename__ = "item_table"
    # Add the id manually
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    plain_text: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String(100), nullable=False)
    updated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    gold_id: Mapped[int] = mapped_column(ForeignKey("gold_table.id"), nullable=False)

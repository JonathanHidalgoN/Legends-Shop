from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class CartTable(base):
    __tablename__ = "cart_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("item_table.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)

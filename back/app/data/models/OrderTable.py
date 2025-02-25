from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class OrderTable(base):
    __tablename__ = "order_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("item_table.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    order_date: Mapped[Date] = mapped_column(Date, nullable=False)


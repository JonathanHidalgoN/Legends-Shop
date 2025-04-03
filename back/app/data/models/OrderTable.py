from sqlalchemy import Column, String, Table, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.models.ItemTable import ItemTable
from app.data.database import base

OrderItemAssociation = Table(
    "order_item_association",
    base.metadata,
    Column("order_id", ForeignKey("order_table.id"), primary_key=True),
    Column("item_id", ForeignKey("item_table.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),
)


class OrderTable(base):
    __tablename__ = "order_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    order_date: Mapped[Date] = mapped_column(Date, nullable=False)
    delivery_date: Mapped[Date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location_table.id"), nullable=False
    )

    items: Mapped[list["ItemTable"]] = relationship(
        "ItemTable",
        secondary=OrderItemAssociation,
    )

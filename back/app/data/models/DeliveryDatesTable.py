from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Table
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base
from app.data.models.ItemTable import ItemTable
from app.data.models.LocationTable import LocationTable

ItemLocationDeliveryAssociation = Table(
    "item_location_delivery_association",
    base.metadata,
    Column("item_id", Integer, ForeignKey("item_table.id"), primary_key=True),
    Column("location_id", Integer, ForeignKey("location_table.id"), primary_key=True),
    Column("delivery_date", Date, nullable=False),
)

class DeliveryDatesTable(base):
    __tablename__ = "delivery_dates_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("item_table.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("location_table.id"), nullable=False)
    delivery_date: Mapped[date] = mapped_column(nullable=False)
    
    item: Mapped["ItemTable"] = relationship("ItemTable")
    location: Mapped["LocationTable"] = relationship("LocationTable")

    def __repr__(self) -> str:
        return f"<DeliveryDatesTable(id={self.id}, item_id={self.item_id}, location_id={self.location_id}, delivery_date={self.delivery_date!r})>" 

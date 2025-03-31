from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base

class LocationTable(base):
    __tablename__ = "location_table"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    country_name: Mapped[str] = mapped_column(unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<LocationTable(id={self.id}, country_name={self.country_name!r})>" 
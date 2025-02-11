from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class MetaDataTable(base):
    __tablename__ = "meta_data_table"
    field_name: Mapped[str] = mapped_column(
        primary_key=True, nullable=False, unique=True
    )
    value: Mapped[str] = mapped_column(nullable=False)

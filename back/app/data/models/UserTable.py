from sqlalchemy import Date, ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class UserTable(base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    userName: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    created: Mapped[Date] = mapped_column(Date, nullable=False)
    last_singn: Mapped[Date] = mapped_column(Date, nullable=False)
    gold_spend: Mapped[int] = mapped_column(nullable=False, default=0)
    current_gold: Mapped[int] = mapped_column(nullable=False, default=0)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    birthdate: Mapped[Date] = mapped_column(Date, nullable=False)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location_table.id"), nullable=False, default=1
    )

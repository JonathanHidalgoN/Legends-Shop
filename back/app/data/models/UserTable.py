from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class UserTable(base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    userName: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)

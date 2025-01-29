from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base


class GoldTable(base):
    __tablename__ = "gold_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_cost: Mapped[int] = mapped_column(nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    sell: Mapped[int] = mapped_column(nullable=False)
    purchaseable: Mapped[bool] = mapped_column(nullable=False)

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base


class GoldTable(declarative_base()):
    __tablename__ = "gold_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base: Mapped[int] = mapped_column(nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    sell: Mapped[int] = mapped_column(nullable=False)
    purchaseable: Mapped[bool] = mapped_column(nullable=False)

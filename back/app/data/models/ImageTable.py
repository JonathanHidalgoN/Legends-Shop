from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base


class ImageTable(declarative_base()):
    __tablename__ = "image_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full: Mapped[str] = mapped_column(nullable=False)
    sprite: Mapped[str] = mapped_column(nullable=False)
    group: Mapped[str] = mapped_column(nullable=False)

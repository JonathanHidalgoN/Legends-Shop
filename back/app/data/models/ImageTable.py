from sqlalchemy.orm import Mapped, mapped_column
from app.data.database import base

class ImageTable(base):
    __tablename__ = "image_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full: Mapped[str] = mapped_column(nullable=False)
    sprite: Mapped[str] = mapped_column(nullable=False)
    group: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ImageTable(id={self.id}, full={self.full!r}, "
            f"sprite={self.sprite!r}, group={self.group!r})>"
        )

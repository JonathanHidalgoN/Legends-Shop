from sqlalchemy import ForeignKey, Integer, Text, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data.database import base


class ReviewTable(base):
    __tablename__ = "review_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("order_table.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("item_table.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 rating
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("order_id", "item_id", name="uix_review_order_item"),
    )

    comments: Mapped[list["CommentTable"]] = relationship(
        "CommentTable", back_populates="review", cascade="all, delete-orphan"
    )


class CommentTable(base):
    __tablename__ = "comment_table"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("review_table.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    review: Mapped["ReviewTable"] = relationship(
        "ReviewTable", back_populates="comments"
    )

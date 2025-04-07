from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.data.models.ReviewTable import ReviewTable, CommentTable
from app.data.models.OrderTable import OrderTable


async def addReview(
    asyncSession: AsyncSession,
    order_id: int,
    item_id: int,
    rating: int,
) -> int:
    """Create a new review."""
    review = ReviewTable(
        order_id=order_id,
        item_id=item_id,
        rating=rating,
    )
    asyncSession.add(review)
    await asyncSession.flush()
    return review.id


async def updateReview(
    asyncSession: AsyncSession,
    review_id: int,
    rating: int,
) -> None:
    """Update a review's rating."""
    review = await getReviewById(asyncSession, review_id)
    if review:
        review.rating = rating
        await asyncSession.flush()
        await asyncSession.commit()


async def getReviewById(
    asyncSession: AsyncSession,
    review_id: int,
) -> Optional[ReviewTable]:
    """Get a review by its ID."""
    result = await asyncSession.execute(
        select(ReviewTable).where(ReviewTable.id == review_id)
    )
    return result.scalar_one_or_none()


async def getReviewsByUserId(
    asyncSession: AsyncSession,
    userId: int,
) -> List[ReviewTable]:
    """Get a review by its ID."""
    result = await asyncSession.execute(
        select(ReviewTable)
        .options(selectinload(ReviewTable.comments))
        .join(OrderTable, OrderTable.id == ReviewTable.order_id)
        .where(OrderTable.user_id == userId)
    )
    return list(result.scalars().all())


async def getReviewsByOrderId(
    asyncSession: AsyncSession,
    order_id: int,
) -> List[ReviewTable]:
    """Get all reviews for a specific order."""
    result = await asyncSession.execute(
        select(ReviewTable).where(ReviewTable.order_id == order_id)
    )
    return list(result.scalars().all())


async def getReviewsByItemId(
    asyncSession: AsyncSession,
    item_id: int,
) -> List[ReviewTable]:
    """Get all reviews for a specific item."""
    result = await asyncSession.execute(
        select(ReviewTable).where(ReviewTable.item_id == item_id)
    )
    return list(result.scalars().all())


async def getReviewsWithCommentsByItemId(
    asyncSession: AsyncSession,
    item_id: int,
) -> List[ReviewTable]:
    """Get all reviews with their comments for a specific item."""
    result = await asyncSession.execute(
        select(ReviewTable)
        .options(selectinload(ReviewTable.comments))
        .where(ReviewTable.item_id == item_id)
    )
    return list(result.scalars().all())


async def addComment(
    asyncSession: AsyncSession,
    review_id: int,
    user_id: int,
    content: str,
) -> None:
    """Create a new comment for a review."""
    comment = CommentTable(
        review_id=review_id,
        user_id=user_id,
        content=content,
    )
    asyncSession.add(comment)
    await asyncSession.flush()


async def updateComment(
    asyncSession: AsyncSession,
    comment_id: int,
    content: str,
) -> None:
    """Update a comment's content."""
    comment = await getCommentById(asyncSession, comment_id)
    if comment:
        comment.content = content
        await asyncSession.flush()
        await asyncSession.commit()


async def getCommentById(
    asyncSession: AsyncSession,
    comment_id: int,
) -> Optional[CommentTable]:
    """Get a comment by its ID."""
    result = await asyncSession.execute(
        select(CommentTable).where(CommentTable.id == comment_id)
    )
    return result.scalar_one_or_none()


async def getCommentsByReviewId(
    asyncSession: AsyncSession,
    review_id: int,
) -> List[CommentTable]:
    """Get all comments for a specific review."""
    result = await asyncSession.execute(
        select(CommentTable).where(CommentTable.review_id == review_id)
    )
    return list(result.scalars().all())


async def getCommentsByUserId(
    asyncSession: AsyncSession,
    user_id: int,
) -> List[CommentTable]:
    """Get all comments made by a specific user."""
    result = await asyncSession.execute(
        select(CommentTable).where(CommentTable.user_id == user_id)
    )
    return list(result.scalars().all())

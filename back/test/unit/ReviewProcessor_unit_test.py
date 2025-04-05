import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.reviews.ReviewProcessor import ReviewProcessor
from app.schemas.Review import Review, Comment
from app.customExceptions import (
    InvalidRatingException,
    InvalidUserReview,
    ReviewProcessorException,
)
from datetime import datetime


@pytest.fixture
def processor() -> ReviewProcessor:
    mockSession = MagicMock(spec=AsyncSession)
    processor = ReviewProcessor(mockSession)
    return processor


@pytest.fixture
def mockReview() -> Review:
    return Review(
        id=1,
        orderId=101,
        itemId=201,
        rating=5,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        comments=[
            Comment(
                id=1, 
                content="Great product!",
                reviewId=1,
                userId=123,
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            )
        ]
    )


@pytest.mark.asyncio
async def test_checkSameUser_success(processor):
    orderId = 101
    userId = 123
    userOrderId = 123 
    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ):
        await processor.checkSameUser(orderId, userId)


@pytest.mark.asyncio
async def test_checkSameUser_failure(processor):
    orderId = 101
    userId = 123
    userOrderId = 456

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ):
        with pytest.raises(InvalidUserReview):
            await processor.checkSameUser(orderId, userId)


@pytest.mark.asyncio
async def test_addReviewAndComments_success(processor, mockReview):
    userId = 123
    reviewId = 301
    userOrderId = 123

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.addReview",
        new=AsyncMock(return_value=reviewId),
    ), patch(
        "app.reviews.ReviewProcessor.addComment",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.reviews.ReviewProcessor.markOrderAsReviewed",
        new=AsyncMock(return_value=None),
    ):
        await processor.addReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_addReviewAndComments_invalidUser(processor, mockReview):
    userId = 123
    userOrderId = 456

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.addReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_addReviewAndComments_invalidRating(processor, mockReview):
    userId = 123
    userOrderId = 123

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.addReview",
        new=AsyncMock(side_effect=InvalidRatingException("Invalid rating")),
    ):
        with pytest.raises(InvalidRatingException):
            await processor.addReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_addReviewAndComments_dbError(processor, mockReview):
    userId = 123
    userOrderId = 123

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.addReview",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.addReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_updateReviewAndComments_success(processor, mockReview):
    userId = 123
    userOrderId = 123
    existingComments = [MagicMock(id=1, content="Old comment")]

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.updateReview",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.reviews.ReviewProcessor.getCommentsByReviewId",
        new=AsyncMock(return_value=existingComments),
    ), patch(
        "app.reviews.ReviewProcessor.updateComment",
        new=AsyncMock(return_value=None),
    ):
        await processor.updateReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_updateReviewAndComments_noExistingComments(processor, mockReview):
    userId = 123
    userOrderId = 123
    existingComments = []

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.updateReview",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.reviews.ReviewProcessor.getCommentsByReviewId",
        new=AsyncMock(return_value=existingComments),
    ), patch(
        "app.reviews.ReviewProcessor.addComment",
        new=AsyncMock(return_value=None),
    ):
        await processor.updateReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_updateReviewAndComments_invalidUser(processor, mockReview):
    userId = 123
    userOrderId = 456

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.updateReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_updateReviewAndComments_dbError(processor, mockReview):
    userId = 123
    userOrderId = 123

    with patch(
        "app.reviews.ReviewProcessor.getUserIdByOrderId",
        new=AsyncMock(return_value=userOrderId),
    ), patch(
        "app.reviews.ReviewProcessor.updateReview",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.updateReviewAndComments(mockReview, userId)


@pytest.mark.asyncio
async def test_getReviewsByUserId_success(processor):
    userId = 123
    mockReviews = [MagicMock(), MagicMock()]
    mappedReviews = [MagicMock(), MagicMock()]

    with patch(
        "app.reviews.ReviewProcessor.getReviewsByUserId",
        new=AsyncMock(return_value=mockReviews),
    ), patch(
        "app.reviews.ReviewProcessor.mapReviewTableToReview",
        side_effect=mappedReviews,
    ):
        result = await processor.getReviewsByUserId(userId)
        assert result == mappedReviews


@pytest.mark.asyncio
async def test_getReviewsByUserId_dbError(processor):
    userId = 123

    with patch(
        "app.reviews.ReviewProcessor.getReviewsByUserId",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.getReviewsByUserId(userId)


@pytest.mark.asyncio
async def test_getReviewsAndCommentsByItemId_success(processor):
    itemId = 201
    mockReviews = [MagicMock(), MagicMock()]
    mappedReviews = [MagicMock(), MagicMock()]

    with patch(
        "app.reviews.ReviewProcessor.getReviewsWithCommentsByItemId",
        new=AsyncMock(return_value=mockReviews),
    ), patch(
        "app.reviews.ReviewProcessor.mapReviewTableToReview",
        side_effect=mappedReviews,
    ):
        result = await processor.getReviewsAndCommentsByItemId(itemId)
        assert result == mappedReviews


@pytest.mark.asyncio
async def test_getReviewsAndCommentsByItemId_dbError(processor):
    itemId = 201

    with patch(
        "app.reviews.ReviewProcessor.getReviewsWithCommentsByItemId",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(ReviewProcessorException):
            await processor.getReviewsAndCommentsByItemId(itemId) 

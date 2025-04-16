from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.database import getDbSession
from app.schemas.Review import Review
from app.reviews.ReviewProcessor import ReviewProcessor
from app.customExceptions import (
    InvalidUserReview,
    ReviewProcessorException,
    InvalidRatingException,
)
from app.routes.auth import getUserIdFromName
from app.rateLimiter import sensitiveRateLimit, apiRateLimit


def getReviewProcessor(
    db: AsyncSession = Depends(getDbSession),
) -> ReviewProcessor:
    return ReviewProcessor(db)


router = APIRouter()


@router.post("/add", status_code=200)
@sensitiveRateLimit()
async def addReview(
    review: Review,
    userId: Annotated[int, Depends(getUserIdFromName)],
    reviewProcessor: ReviewProcessor = Depends(getReviewProcessor),
):
    try:
        await reviewProcessor.addReviewAndComments(review, userId)
        return {"message": "Review added successfully"}
    except InvalidRatingException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidUserReview as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ReviewProcessorException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", status_code=200)
async def updateReview(
    review: Review,
    userId: Annotated[int, Depends(getUserIdFromName)],
    reviewProcessor: ReviewProcessor = Depends(getReviewProcessor),
):
    """
    Update an existing review and its comments.

    This endpoint allows users to update their existing reviews, including the rating and comments.
    The user must be the owner of the order associated with the review.
    """
    try:
        await reviewProcessor.updateReviewAndComments(review, userId)
        return {"message": "Review updated successfully"}
    except InvalidRatingException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidUserReview as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ReviewProcessorException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user", status_code=200, response_model=List[Review])
@apiRateLimit()
async def getReviewsByUserId(
    userId: Annotated[int, Depends(getUserIdFromName)],
    reviewProcessor: ReviewProcessor = Depends(getReviewProcessor),
):
    """
    Get all reviews for the authenticated user.

    This endpoint retrieves all reviews and their associated comments for the currently authenticated user.
    """
    try:
        reviews = await reviewProcessor.getReviewsByUserId(userId)
        return reviews
    except ReviewProcessorException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{item_id}", status_code=200, response_model=List[Review])
async def getReviewsByItemId(
    item_id: int,
    reviewProcessor: ReviewProcessor = Depends(getReviewProcessor),
):
    """
    Get all reviews for a specific item.

    This endpoint retrieves all reviews and their associated comments for a specific item.
    No authentication is required to access this endpoint.

    Args:
        item_id (int): The ID of the item whose reviews to retrieve

    Returns:
        List[Review]: A list of reviews with their associated comments
    """
    try:
        reviews = await reviewProcessor.getReviewsAndCommentsByItemId(item_id)
        return reviews
    except ReviewProcessorException as e:
        raise HTTPException(status_code=500, detail=str(e))

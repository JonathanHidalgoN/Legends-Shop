from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.database import getDbSession
from app.schemas.Review import Review
from app.reviews.ReviewProcessor import ReviewProcessor
from app.customExceptions import InvalidUserReview, ReviewProcessorException, InvalidRatingException
from app.routes.auth import getUserIdFromName


def getReviewProcessor(
    db: AsyncSession = Depends(getDbSession),
) -> ReviewProcessor:
    return ReviewProcessor(db)


router = APIRouter()


@router.post("/add", status_code=200)
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

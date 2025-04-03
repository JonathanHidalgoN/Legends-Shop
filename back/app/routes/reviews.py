from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.database import getDbSession
from app.schemas.Review import Review
from app.reviews.ReviewProcessor import ReviewProcessor
from app.customExceptions import InvalidUserReview, ReviewProcessorException, InvalidRatingException
from back.app.routes.auth import getUserIdFromName


def getReviewProcessor(
    db: AsyncSession = Depends(getDbSession),
) -> ReviewProcessor:
    return ReviewProcessor(db)


router = APIRouter()


@router.post("/", status_code=200)
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

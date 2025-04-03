from datetime import datetime
from typing import Annotated, List
from pydantic import AfterValidator, BaseModel
from app.customExceptions import InvalidRatingException

def validateRating(rating:int)->int:
        if not 1 <= rating <= 5:
            raise InvalidRatingException("Rating must be between 1 and 5")
        return rating


class Comment(BaseModel):
    id: int
    reviewId: int
    userId: int
    content: str
    createdAt: datetime
    updatedAt: datetime


class Review(BaseModel):
    id: int
    orderId: int
    itemId: int
    rating: Annotated[int, AfterValidator(validateRating)]
    createdAt: datetime
    updatedAt: datetime
    comments: List[Comment] = [] 

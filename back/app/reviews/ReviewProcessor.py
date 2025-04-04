from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.Review import Review
from sqlalchemy.exc import SQLAlchemyError
from app.auth.functions import logMethod
from app.customExceptions import InvalidRatingException, InvalidUserReview, ReviewProcessorException
from app.data.queries.reviewQueries import addReview, getReviewsByUserId, getCommentsByUserId
from app.data.queries.reviewQueries import addComment
from app.data.queries.orderQueries import getUserIdByOrderId, markOrderAsReviewed
from app.data.mappers import mapReviewTableToReview, mapCommentTableToComment
from typing import List


class ReviewProcessor:
    def __init__(self, dbSession: AsyncSession) -> None:
        self.dbSession = dbSession 

    @logMethod
    async def checkSameUser(self, orderId:int, userId:int)->None:
        userOrderId:int | None = await getUserIdByOrderId(self.dbSession, orderId)
        if userId != userOrderId:
            raise InvalidUserReview("User is different to the order user")

    @logMethod
    async def addReviewAndComments(self, review: Review, userId:int) -> None:
        try:
            await self.checkSameUser(review.orderId, userId)
            reviewId:int = await addReview(self.dbSession, 
                                           review.orderId, review.itemId, review.rating) 
            for comment in review.comments:
                await addComment(self.dbSession, reviewId, userId, comment.content)

            await markOrderAsReviewed(self.dbSession, review.orderId)
        except InvalidRatingException as e:
            await self.dbSession.rollback()
            raise e
        except (Exception,SQLAlchemyError) as e:
            await self.dbSession.rollback()
            raise ReviewProcessorException("Internal server error") from e
            
    @logMethod
    async def getReviewsByUserId(self, userId: int) -> List[Review]:
        """
        Get all reviews and their comments for a specific user.
        
        Args:
            userId (int): The ID of the user whose reviews to retrieve
            
        Returns:
            List[Review]: A list of reviews with their associated comments
        """
        try:
            reviews = await getReviewsByUserId(self.dbSession, userId)
            mapped_reviews = [mapReviewTableToReview(review) for review in reviews]
            
            return mapped_reviews
        except SQLAlchemyError as e:
            raise ReviewProcessorException("Error retrieving reviews") from e

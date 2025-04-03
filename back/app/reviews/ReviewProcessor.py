from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.Review import Review
from sqlalchemy.exc import SQLAlchemyError
from app.auth.functions import logMethod
from app.customExceptions import InvalidRatingException, InvalidUserReview, ReviewProcessorException
from app.data.queries.reviewQueries import addReview
from app.data.queries.reviewQueries import addComment
from back.app.data.queries.orderQueries import getUserIdByOrderId


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
        except InvalidRatingException as e:
            await self.dbSession.rollback()
            raise e
        except (Exception,SQLAlchemyError) as e:
            await self.dbSession.rollback()
            raise ReviewProcessorException("Internal server error") from e

from typing import List, Tuple
from app.customExceptions import ProfileWorkerException, UserNoGoldRow
from app.data.queries.profileQueries import getCurrentUserGoldWithUserName
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError

from app.data.queries.authQueries import getUserInDB
from app.data.queries.orderQueries import getUniqueItemNamesQuantityAndBasePriceByUserName
from app.schemas.AuthSchemas import UserInDB
from app.schemas.Order import OrderSummary
from app.schemas.profileSchemas import ProfileInfo


class ProfileWorker:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    async def getUserGoldWithUserName(self, userName: str) -> int:
        logger.debug(f"Getting {userName} gold from database")
        try:
            gold: int | None = await getCurrentUserGoldWithUserName(
                self.dbSession, userName
            )
        except SQLAlchemyError as e:
            logger.error(f"Error, sqlalchemy error: {e}")
            raise ProfileWorkerException("SQLAlchemyError") from e
        except Exception as e:
            raise ProfileWorkerException(
                "Unexpected exception while getting user gold"
            ) from e
        if gold is None:
            logger.error(
                f"Error, the user {userName} has no gold in row in the database"
            )
            raise UserNoGoldRow()
        logger.debug(f"{userName} has {gold} in the database")
        return gold

    async def getProfileInfo(self, userName:str) -> ProfileInfo:
        logger.debug(f"Getting {userName} profile info from database")
        try:
            user: UserInDB | None = await getUserInDB(self.dbSession, userName)
            if user is None:
                logger.error(f"{userName} information can not be None, this a internal error")
                raise ProfileWorkerException("None value in user info")
            orderSummaryList: List[OrderSummary] = await self.buildOrderSummaryForUser(userName)
            return ProfileInfo(user=user, ordersInfo=orderSummaryList)
        except SQLAlchemyError as e:
            logger.error(f"Error getting user {userName} information, exception: {e}")
            raise ProfileWorkerException("SQLAlchemyError") from e

    async def buildOrderSummaryForUser(self, userName:str) -> List[OrderSummary]:
        logger.debug(f"Building {userName} order summary")
        try:
            logger.debug(f"Getting {userName} ordered items and base price")
            itemNameAndCostOrderedByUser : List[OrderSummary] = await getUniqueItemNamesQuantityAndBasePriceByUserName(self.dbSession, userName)
            logger.debug(f"{userName} ordered summary and base price info obtained successfully")
            return itemNameAndCostOrderedByUser
        except SQLAlchemyError as e:
            logger.debug(f"Getting {userName} profile info from database")
            raise ProfileWorkerException("SQLAlchemyError") from e



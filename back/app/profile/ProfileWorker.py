from typing import List, Tuple
from app.customExceptions import ProfileWorkerException, UserNoGoldRow
from app.data.queries.profileQueries import getCurrentUserGoldWithUserName
from sqlalchemy.exc import SQLAlchemyError

from app.data.queries.authQueries import getUserInDB
from app.data.queries.orderQueries import (
    getUniqueItemNamesQuantityAndBasePriceByUserName,
)
from app.schemas.AuthSchemas import UserInDB
from app.schemas.Order import OrderSummary
from app.schemas.profileSchemas import ProfileInfo
from app.logger import logMethod


class ProfileWorker:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    @logMethod
    async def getUserGoldWithUserName(self, userName: str) -> int:
        try:
            gold: int | None = await getCurrentUserGoldWithUserName(
                self.dbSession, userName
            )
        except SQLAlchemyError as e:
            raise ProfileWorkerException("SQLAlchemyError") from e
        except Exception as e:
            raise ProfileWorkerException(
                "Unexpected exception while getting user gold"
            ) from e
        if gold is None:
            raise UserNoGoldRow()
        return gold

    @logMethod
    async def getProfileInfo(self, userName: str) -> ProfileInfo:
        try:
            user: UserInDB | None = await getUserInDB(self.dbSession, userName)
            if user is None:
                raise ProfileWorkerException("None value in user info")
            user.hashedPassword = ""
            orderSummaryList: List[OrderSummary] = await self.buildOrderSummaryForUser(
                userName
            )
            return ProfileInfo(user=user, ordersInfo=orderSummaryList)
        except SQLAlchemyError as e:
            raise ProfileWorkerException("SQLAlchemyError") from e

    @logMethod
    async def buildOrderSummaryForUser(self, userName: str) -> List[OrderSummary]:
        try:
            itemNameAndCostOrderedByUser: List[OrderSummary] = (
                await getUniqueItemNamesQuantityAndBasePriceByUserName(
                    self.dbSession, userName
                )
            )
            return itemNameAndCostOrderedByUser
        except SQLAlchemyError as e:
            raise ProfileWorkerException("SQLAlchemyError") from e

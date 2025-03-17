from app.customExceptions import ProfileWorkerException, UserNoGoldRow
from app.data.queries.profileQueries import getCurrentUserGoldWithUserName
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError

class ProfileWorker:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    async def getUserGoldWithUserName(self,userName:str)->int:
        logger.debug(f"Getting {userName} gold from database")
        try:
            gold : int | None = await getCurrentUserGoldWithUserName(self.dbSession, userName)
        except SQLAlchemyError as e:
            logger.error(f"Error, sqlalchemy error: {e}")
            raise ProfileWorkerException("SQLAlchemyError") from e
        except Exception as e:
            raise ProfileWorkerException("Unexpected exception while getting user gold") from e
        if gold is None:
            logger.error(f"Error, the user {userName} has no gold in row in the database")
            raise UserNoGoldRow()
        logger.debug(f"{userName} has {gold} in the database")
        return gold

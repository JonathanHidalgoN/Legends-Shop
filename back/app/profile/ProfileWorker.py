from back.app.customExceptions import ProfileWorkerException, UserNoGoldRow
from back.app.data.queries.profileQueries import getUserGoldWithUserName
from app.logger import logger
from sqlalchemy.exc import SQLAlchemyError

class ProfileWorker:

    def __init__(self, dbSession) -> None:
        self.dbSession = dbSession
        pass

    async def getUserGoldWithUserName(self,userName:str)->int:
        try:
            logger.debug(f"Getting {userName} gold from database")
            gold : int | None = await getUserGoldWithUserName(self.dbSession, userName)
            if gold is None:
                logger.error(f"Error, the user {userName} has no gold in row in the database")
                raise UserNoGoldRow()
            logger.debug(f"{userName} has {gold} in the database")
            return gold
        except SQLAlchemyError as e:
            logger.error(f"Error, sqlalchemy error: {e}")
            raise ProfileWorkerException("SQLAlchemyError") from e
        except Exception as e:
            raise ProfileWorkerException("Unexpected exception while getting user gold") from e

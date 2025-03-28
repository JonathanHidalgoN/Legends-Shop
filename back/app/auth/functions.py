import functools
import asyncio
from passlib.context import CryptContext
from jose import JWSError, jwt
from datetime import datetime, timedelta, timezone
from app.envVariables import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.logger import logger

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)


def hashPassword(password: str) -> str:
    return pwdContext.hash(password)


def createAccessToken(data: dict) -> str:
    toEncode = data.copy()
    expire: datetime = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    toEncode.update({"exp": expire})
    encodedJwt: str = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJwt


def verifyToken(token: str) -> str | None:
    try:
        content = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userName = content.get("sub")
        if userName is None:
            return None
        return userName
    except JWSError:
        return None


def logMethod(func):
    """Decorator to log function call, success, and error with class name and arguments."""

    @functools.wraps(func)
    async def asyncWrapper(*args, **kwargs):
        className = args[0].__class__.__name__ if args else ""
        funcName = func.__name__
        logger.debug(
            f"{className} - {funcName} called with args: {args[1:]}, kwargs: {kwargs}"
        )
        try:
            result = await func(*args, **kwargs)
            logger.debug(
                f"{className} - {funcName} called with args: {args[1:]}, kwargs: {kwargs} returned successfully."
            )
            return result
        except Exception as e:
            logger.error(
                f"{className} - {funcName} error with args: {args[1:]}, kwargs: {kwargs} - {e}",
                exc_info=True,
            )
            raise

    @functools.wraps(func)
    def syncWrapper(*args, **kwargs):
        className = args[0].__class__.__name__ if args else ""
        funcName = func.__name__
        logger.debug(
            f"{className} - {funcName} called with args: {args[1:]}, kwargs: {kwargs}"
        )
        try:
            result = func(*args, **kwargs)
            logger.debug(
                f"{className} - {funcName} called with args: {args[1:]}, kwargs: {kwargs} returned successfully."
            )
            return result
        except Exception as e:
            logger.error(
                f"{className} - {funcName} error with args: {args[1:]}, kwargs: {kwargs} - {e}",
                exc_info=True,
            )
            raise

    if asyncio.iscoroutinefunction(func):
        return asyncWrapper
    else:
        return syncWrapper

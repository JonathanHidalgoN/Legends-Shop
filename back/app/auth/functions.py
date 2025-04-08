from passlib.context import CryptContext
from jose import JWSError, jwt
from datetime import datetime, timedelta, timezone
from app.envVariables import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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

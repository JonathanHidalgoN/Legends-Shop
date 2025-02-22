from fastapi import Depends
from passlib.context import CryptContext
from jose import JWSError, jwt
from datetime import datetime, timedelta, timezone

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY : str = "b8281551b3bc6382348db701e6d33a4cc8644c179714dda69e29ba574e7f7bf7"
ALGORITHM : str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verifyPassword(plainPassword: str, hashedPassword:str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)

def hashPassword(password:str)-> str:
    return pwdContext.hash(password)

def createAccessToken(data:dict)-> str:
    toEncode = data.copy()
    expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode.update({"exp":expire})
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


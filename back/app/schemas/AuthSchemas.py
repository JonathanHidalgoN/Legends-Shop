from pydantic import BaseModel
from datetime import date


class User(BaseModel):
    userName: str
    email:str
    created:date
    lastSingin:date
    goldSpend:int
    currentGold:int
    birthDate:date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    userName: str | None = None


class UserInDB(User):
    hashedPassword: str

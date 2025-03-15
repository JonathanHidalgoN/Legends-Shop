from pydantic import BaseModel


class User(BaseModel):
    userName: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    userName: str | None = None


class UserInDB(User):
    hashedPassword: str

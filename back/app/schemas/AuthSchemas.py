import re
from enum import Enum
from typing import Annotated
from pydantic import AfterValidator, BaseModel
from datetime import date

from app.customExceptions import InvalidUserEmailException, InvalidUserGoldFieldException, InvalidUserNameException

def userNameValidation(userName:str)->str:
    MIN_LEN : int = 8 
    if len(userName) < MIN_LEN:
        raise InvalidUserNameException(f"Error, userName has to be {MIN_LEN} characters at least")
    return userName

def emailValidation(email:str)->str:
    if re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$",email):
        return email
    raise InvalidUserEmailException(f"Email {email} do not match email pattern")

def isPositive(number:int)->int:
    if number >=0:
        return number
    raise InvalidUserGoldFieldException(f"Number {number} should be positive")

class User(BaseModel):
    userName: Annotated[str, AfterValidator(userNameValidation)] 
    email: Annotated[str, AfterValidator(emailValidation)] 
    created: date
    lastSingIn: date
    goldSpend: Annotated[int, AfterValidator(isPositive)] 
    currentGold: Annotated[int, AfterValidator(isPositive)]
    birthDate: date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    userName: str | None = None


class UserInDB(User):
    hashedPassword: str


class SingUpError(str, Enum):
    USERNAMEEXIST = "USERNAMEEXIST"
    EMAILEXIST = "EMAILEXIST"
    INVALIDEMAIL = "INVALIDEMAIL"
    INVALIDDATE = "INVALIDDATE"
    INVALIDUSERNAME = "INVALIDUSERNAME"
    INVALIDUSERGOLD = "INVALIDUSERGOLD"

class LogInError(str, Enum):
    INVALIDUSERNAME = "INVALIDUSERNAME"
    INVALIDPASSWORD = "INVALIDPASSWORD"
    INCORRECTCREDENTIALS = "INCORRECTCREDENTIALS"
    INTERNALSERVERERROR="INTERNALSERVERERROR"

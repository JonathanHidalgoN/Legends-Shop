from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.functions import (
    createAccessToken,
    verifyPassword,
    verifyToken,
    hashPassword,
)
from app.data import database
from app.data.queries.authQueries import checkUserExistInDB, getUserInDB, insertUser
from app.schemas.AuthSchemas import Token, UserInDB, singUpRequest
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# Source:https://fastapi.tiangolo.com/tutorial/security/first-steps/#create-mainpy
router = APIRouter()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def getCurrentUser(token: Annotated[str, Depends(oauth2Scheme)]):
    userName: str | None = verifyToken(token)
    if not userName:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WW-Authenticate": "Bearer"},
        )
    return userName


# https://stackoverflow.com/questions/65059811/what-does-depends-with-no-parameter-do
@router.post("/token", response_model=Token)
async def getToken(
    response:Response,
    dataForm: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        matchUser: UserInDB | None = await getUserInDB(db, dataForm.username)
    except Exception:
        raise HTTPException(
            status_code=500, detail="Error retriving the user from the server"
        )
    if not matchUser:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verifyPassword(dataForm.password, matchUser.hashedPassword):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    accessToken = createAccessToken(data={"sub": matchUser.userName})
    response.set_cookie(
        key="accessToken",
        value=accessToken,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60*30,
        path="/"
    )
    return {"access_token": accessToken, "token_type": "bearer"}


@router.get("/test")
async def protectTest(user: Annotated[str, Depends(getCurrentUser)]):
    return {"message": user}

@router.post("/singUp")
async def singUp(
    userData: singUpRequest, db: AsyncSession = Depends(database.getDbSession)
):
    try:
        userExist: bool = await checkUserExistInDB(db, userData.username)
    except Exception:
        raise HTTPException(
            status_code=400, detail="Error retriving the user from the server"
        )
    if userExist:
        raise HTTPException(status_code=500, detail="Username exist, change it")
    userInDB: UserInDB = UserInDB(
        userName=userData.username, hashedPassword=hashPassword(userData.password)
    )
    try:
        await insertUser(db, userInDB)
        return {"message": "nice"}
    except Exception:
        raise HTTPException(status_code=500, detail="Server error inserting the user")

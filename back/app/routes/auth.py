from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import UserIdNotFound
from app.logger import logger
from app.auth.functions import (
    createAccessToken,
    verifyPassword,
    verifyToken,
    hashPassword,
)
from app.data import database
from app.data.queries.authQueries import (
    checkUserExistInDB,
    getUserIdWithUserName,
    getUserInDB,
    insertUser,
)
from app.schemas.AuthSchemas import UserInDB
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# Source:https://fastapi.tiangolo.com/tutorial/security/first-steps/#create-mainpy
router = APIRouter()
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def getCurrentUserTokenFlow(request: Request):
    logger.debug(f"Request to {request.url.path}, checking token...")
    token: str | None = request.cookies.get("access_token")
    if token is None:
        logger.error(f"Error in {request.url.path} token is None")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WW-Authenticate": "Bearer"},
        )
    userName: str | None = verifyToken(token)
    if not userName:
        logger.error(f"Error in {request.url.path} invalid token")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WW-Authenticate": "Bearer"},
        )
    logger.debug(f"Request to {request.url.path}, authenticated")
    return userName


async def getUserIdFromName(
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    db: AsyncSession = Depends(database.getDbSession),
) -> int:
    userId: int | None = await getUserIdWithUserName(db, userName)
    if userId is None:
        raise UserIdNotFound(userName, f"User {userName} not found in database")
    return userId


# https://stackoverflow.com/questions/65059811/what-does-depends-with-no-parameter-do
@router.post("/token")
async def getToken(
    request: Request,
    response: Response,
    dataForm: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        logger.debug(f"Request to {request.url.path}, authenticating...")
        matchUser: UserInDB | None = await getUserInDB(db, dataForm.username)
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected exception: {e}")
        raise HTTPException(
            status_code=500, detail="Error retriving the user from the server"
        )
    if not matchUser:
        logger.error(f"Error in {request.url.path}, {dataForm.username} do not exit")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not verifyPassword(dataForm.password, matchUser.hashedPassword):
        logger.error(
            f"Error in {request.url.path}, incorrect password for user {dataForm.username}"
        )
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    accessToken = createAccessToken(data={"sub": matchUser.userName})
    response.set_cookie(
        key="access_token",
        value=accessToken,
        httponly=True,
        # TODO: change this to true when working on https
        secure=False,
        # secure=True,
        samesite="lax",
        max_age=60 * 30,
        path="/",
    )
    logger.debug(f"Request to {request.url.path} completed successfully")


@router.get("/token_refresh")
async def tokenRefresh(
    request: Request,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    response: Response,
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        logger.debug(f"Request to {request.url.path}")
        matchUser: UserInDB | None = await getUserInDB(db, userName)
        if not matchUser:
            logger.error(f"Error in {request.url.path}, {userName} do not exit")
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        logger.debug(f"Request to {request.url.path} completed successfully")
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected error {e}")
        raise HTTPException(status_code=500, detail="Error login out")
    accessToken = createAccessToken(data={"sub": matchUser.userName})
    response.set_cookie(
        key="access_token",
        value=accessToken,
        httponly=True,
        # TODO: change this to true when working on https
        secure=False,
        # secure=True,
        samesite="lax",
        max_age=60 * 30,
        path="/",
    )
    logger.debug(
        f"Request to {request.url.path} completed successfully, token in response"
    )


@router.post("/singup")
async def singUp(
    request: Request,
    #This ... makes required in fastapi
    username:str = Form(...),
    password:str = Form(...),
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        logger.debug(f"Request to {request.url.path}")
        userExist: bool = await checkUserExistInDB(db, username)
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected exception: {e}")
        raise HTTPException(
            status_code=500, detail="Error retriving the user from the server"
        )
    if userExist:
        logger.error(
            f"Error in {request.url.path}, the {username} already exist"
        )
        raise HTTPException(status_code=400, detail="Username exist, change it")
    userInDB: UserInDB = UserInDB(
        userName=username, hashedPassword=hashPassword(password)
    )
    try:
        await insertUser(db, userInDB)
        logger.debug(f"Request to {request.url.path} completed successfully")
        return {"message": "nice"}
    except Exception as e:
        logger.error(
            f"Error in {request.url.path}, unexpected error inserting new user with userName {username}, exception: {e}"
        )
        raise HTTPException(status_code=500, detail="Server error inserting the user")


@router.get("/logout")
async def logoutRequest(request: Request, response: Response):
    try:
        logger.debug(f"Request to {request.url.path}")
        response.delete_cookie("access_token", path="/")
        logger.debug(f"Request to {request.url.path} completed successfully")
        return {"detail": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected error {e}")
        raise HTTPException(status_code=500, detail="Error login out")

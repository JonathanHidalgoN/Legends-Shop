from datetime import datetime
import re
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    InvalidPasswordException,
    InvalidUserEmailException,
    InvalidUserGoldFieldException,
    InvalidUserNameException,
    UserIdNotFound,
)
from app.logger import logger
from app.auth.functions import (
    createAccessToken,
    verifyPassword,
    verifyToken,
    hashPassword,
)
from app.data import database
from app.data.queries.authQueries import (
    checkEmailExistInDB,
    checkUserExistInDB,
    getUserIdWithUserName,
    getUserInDB,
    insertUser,
)
from app.schemas.AuthSchemas import LogInError, SingUpError, UserInDB
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.data.queries.profileQueries import updateLastSingInWithUserName

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
            status_code=500,
            detail="Error retriving the user from the server",
            headers={
                "X-Error-Type": LogInError.INTERNALSERVERERROR,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    if not matchUser:
        logger.error(f"Error in {request.url.path}, {dataForm.username} do not exit")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={
                "X-Error-Type": LogInError.INCORRECTCREDENTIALS,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    if not verifyPassword(dataForm.password, matchUser.hashedPassword):
        logger.error(
            f"Error in {request.url.path}, incorrect password for user {dataForm.username}"
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={
                "X-Error-Type": LogInError.INCORRECTCREDENTIALS,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
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
    await updateLastSingInWithUserName(db, dataForm.username, datetime.now().date())
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
                status_code=401, detail="Incorrect username or password"
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
    await updateLastSingInWithUserName(db, userName, datetime.now().date())
    logger.debug(
        f"Request to {request.url.path} completed successfully, token in response"
    )


@router.post("/singup")
async def singUp(
    request: Request,
    # This ... makes required in fastapi
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    birthDate: str = Form(...),
    db: AsyncSession = Depends(database.getDbSession),
):
    logger.debug(f"Request to {request.url.path}")

    try:
        birthDateDate = datetime.strptime(birthDate, "%Y-%m-%d")
        userInDB: UserInDB = UserInDB(
            userName=username,
            hashedPassword=hashPassword(password),
            created=datetime.now().date(),
            email=email,
            goldSpend=0,
            currentGold=99999,
            birthDate=birthDateDate,
            lastSingIn=datetime.now().date(),
            password=password,
        )
        userExist: bool = await checkUserExistInDB(db, username)
        emailExist: bool = await checkEmailExistInDB(db, email)
    except InvalidUserNameException as e:
        logger.error(f"Error in {request.url.path}, exception: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={
                "X-Error-Type": SingUpError.INVALIDUSERNAME,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    except InvalidPasswordException as e:
        logger.error(f"Error in {request.url.path}, exception: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={
                "X-Error-Type": SingUpError.INVALIDPASSWORD,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    except InvalidUserEmailException as e:
        logger.error(f"Error in {request.url.path}, exception: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={
                "X-Error-Type": SingUpError.INVALIDEMAIL,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    except InvalidUserGoldFieldException as e:
        logger.error(f"Error in {request.url.path}, exception: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
            headers={
                "X-Error-Type": SingUpError.INVALIDUSERGOLD,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    except ValueError as e:
        logger.error(f"Error in {request.url.path}, exception: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid date value",
            headers={
                "X-Error-Type": SingUpError.INVALIDDATE,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected exception: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
            headers={
                "X-Error-Type": SingUpError.INTERNALSERVERERROR,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    if userExist:
        logger.error(
            f"Error in {request.url.path}, the username {username} already exist"
        )
        raise HTTPException(
            status_code=400,
            detail="Username exist, change it",
            headers={
                "X-Error-Type": SingUpError.USERNAMEEXIST,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
        )
    if emailExist:
        logger.error(f"Error in {request.url.path}, the email {email} already exist")
        raise HTTPException(
            status_code=400,
            detail="Email exist, change it",
            headers={
                "X-Error-Type": SingUpError.EMAILEXIST,
                "Access-Control-Expose-Headers": "X-Error-Type",
            },
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

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger

from app.routes.auth import getCurrentUserTokenFlow

from app.data import database
from app.customExceptions import ProfileWorkerException
from app.profile.ProfileWorker import ProfileWorker
from app.schemas.profileSchemas import ProfileGoldResponse, ProfileInfo

router = APIRouter()


def getProfileWorker(
    db: AsyncSession = Depends(database.getDbSession),
) -> ProfileWorker:
    return ProfileWorker(db)


@router.get("/current_gold", response_model=ProfileGoldResponse)
async def getUserGold(
    request: Request,
    profileWorker: Annotated[ProfileWorker, Depends(getProfileWorker)],
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
):
    try:
        userGold: int = await profileWorker.getUserGoldWithUserName(userName)
        return {"userGold": userGold}
    except ProfileWorkerException:
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/info", response_model=ProfileInfo)
async def getProfileInfo(
    request: Request,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    profileWorker: Annotated[ProfileWorker, Depends(getProfileWorker)],
):
    try:
        profileInfo: ProfileInfo = await profileWorker.getProfileInfo(userName)
        return profileInfo
    except ProfileWorkerException:
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Error in {request.url.path}, unexpected error {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

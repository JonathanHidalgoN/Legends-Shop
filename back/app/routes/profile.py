from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger

from app.routes.auth import getCurrentUserTokenFlow

from app.data import database
from app.customExceptions import ProfileWorkerException
from app.profile.ProfileWorker import ProfileWorker
from app.schemas.profileSchemas import UserGoldResponse

router = APIRouter()


def getProfileWorker(
    db: AsyncSession = Depends(database.getDbSession),
) -> ProfileWorker:
    return ProfileWorker(db)


@router.get("/current_gold", response_model=UserGoldResponse)
async def getUserGold(
    request: Request,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    profileWorker: Annotated[ProfileWorker, Depends(getProfileWorker)],
):
    try:
        logger.debug(f"Request to {request.url.path} from user {userName}")
        userGold: int = await profileWorker.getUserGoldWithUserName(userName)
        logger.debug(f"Request to {request.url.path} completed")
        return {"userGold": userGold}
    except ProfileWorkerException:
        raise HTTPException(status_code=500, detail="Internal server error")

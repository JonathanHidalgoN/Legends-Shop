from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger

from app.routes.auth import getCurrentUserTokenFlow

from app.data import database
from back.app.customExceptions import ProfileWorkerException
from back.app.profile.ProfileWorker import ProfileWorker

router = APIRouter()

def getProfileWorker(
    db: AsyncSession = Depends(database.getDbSession),
) -> ProfileWorker:
    return ProfileWorker(db)

@router.post("/get_gold")
async def getUserGold(
    request: Request,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    profileWorker: Annotated[ProfileWorker, Depends(getProfileWorker)]
):
    try:
        logger.debug(f"Request to {request.url.path} from user {userName}")
        userGold : int = await profileWorker.getUserGoldWithUserName(userName)
        logger.debug(f"Request to {request.url.path} completed")
        return {"user_gold": userGold}
    except ProfileWorkerException:
        raise HTTPException(status_code=500, detail="Internal server error")


from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger
from app.data import database
from app.routes.auth import getCurrentUserTokenFlow

router = APIRouter()

@router.get("/order")
async def test(
    request: Request, 
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    db: AsyncSession = Depends(database.getDbSession)
):
    return {"message": f"Hello {userName}"}

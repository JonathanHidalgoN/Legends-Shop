from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger
from app.data import database
from app.routes.auth import getCurrentUserTokenFlow
from app.schemas.Order import Order

router = APIRouter()

@router.post("/order")
async def order(
    request: Request, 
    order: Order,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    db: AsyncSession = Depends(database.getDbSession)
):
    return {"message": f"{order} {userName}"}

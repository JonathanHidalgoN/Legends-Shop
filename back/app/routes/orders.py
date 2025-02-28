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


@router.post("/test")
async def test(
    request: Request, 
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    db: AsyncSession = Depends(database.getDbSession)
):
    return {"message": f"Hello {userName}"}

@router.post("/test2")
async def test2(
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
):
    return {"message": f"{userName}"}


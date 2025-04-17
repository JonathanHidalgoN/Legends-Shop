from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    NotEnoughGoldException,
    ProcessOrderException,
    UserIdNotFound,
)
from app.logger import logger
from app.data import database
from app.orders.OrderProcessor import OrderProcessor
from app.routes.auth import getUserIdFromName
from app.schemas.Order import Order
from app.rateLimiter import sensitiveRateLimit, apiRateLimit

router = APIRouter()


def getOrderProcessor(
    db: AsyncSession = Depends(database.getDbSession),
) -> OrderProcessor:
    return OrderProcessor(db)


@router.post("/order", response_model=int)
@sensitiveRateLimit()
async def order(
    request: Request,
    order: Order,
    userId: Annotated[int, Depends(getUserIdFromName)],
    orderProcessor: Annotated[OrderProcessor, Depends(getOrderProcessor)],
):
    try:
        orderId: int = await orderProcessor.makeOrder(order, userId)
    except (InvalidItemException, DifferentTotal, NotEnoughGoldException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (UserIdNotFound, ProcessOrderException) as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected exception")
    return orderId


@router.get("/order_history", response_model=List[Order])
async def getOrderHistory(
    request: Request,
    userId: Annotated[int, Depends(getUserIdFromName)],
    orderProcessor: Annotated[OrderProcessor, Depends(getOrderProcessor)],
):
    try:
        orders: List[Order] = await orderProcessor.getOrderHistory(userId)
        return orders
    except ProcessOrderException as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/cancel_order/{order_id}", response_model=None)
async def cancelOrder(
    request: Request,
    order_id: int,
    userId: Annotated[int, Depends(getUserIdFromName)],
    orderProcessor: Annotated[OrderProcessor, Depends(getOrderProcessor)],
):
    try:
        await orderProcessor.cancelOrder(userId, order_id)
    except ProcessOrderException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

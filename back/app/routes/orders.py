from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    ProcessOrderException,
    UserIdNotFound,
)
from app.data.queries.orderQueries import getOrderHistoryQuery
from app.logger import logger
from app.data import database
from app.orders.OrderProcessor import OrderProcessor
from app.routes.auth import getUserIdFromName
from app.schemas.Order import Order

router = APIRouter()


def getOrderProcessor(
    db: AsyncSession = Depends(database.getDbSession),
) -> OrderProcessor:
    return OrderProcessor(db)


@router.post("/order")
async def order(
    request: Request,
    order: Order,
    userId: Annotated[int, Depends(getUserIdFromName)],
    orderProcessor: Annotated[OrderProcessor, Depends(getOrderProcessor)],
):
    try:
        logger.debug(f"Request to {request.url.path}")
        orderId: int = await orderProcessor.makeOrder(order, userId)
    except (InvalidItemException, DifferentTotal) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (UserIdNotFound, ProcessOrderException) as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected exception")
    logger.debug(f"Request to {request.url.path} completed")
    return {"order_id": f"{orderId}"}


@router.get("/order_history", response_model=List[Order])
async def getOrderHistory(
    request: Request,
    userId: Annotated[int, Depends(getUserIdFromName)],
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        logger.debug(f"Request to {request.url.path}")
        orders: List[Order] = await getOrderHistoryQuery(db, userId)
        logger.debug(f"Request to {request.url.path} completed")
        return orders
    except Exception as e:
        logger.error(f"Request to {request.url.path} caused exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

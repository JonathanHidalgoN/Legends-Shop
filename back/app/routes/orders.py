from datetime import date
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    DifferentTotal,
    InvalidItemException,
    NotEnoughGoldException,
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
        logger.debug(f"Request to {request.url.path} from user {userId}")
        orderId: int = await orderProcessor.makeOrder(order, userId)
    except (InvalidItemException, DifferentTotal, NotEnoughGoldException) as e:
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
    orderStatus: str = Query("ALL"),
    minOrderDate: Optional[date] = Query(None),
    maxOrderDate: Optional[date] = Query(None),
    minDeliveryDate: Optional[date] = Query(None),
    maxDeliveryDate: Optional[date] = Query(None),
    sortField: Optional[str] = Query(None),
    sortOrder: Optional[str] = Query(None),
    filterItemNames: Optional[str] = Query(None),
    db: AsyncSession = Depends(database.getDbSession),
):
    try:
        logger.debug(f"Request to {request.url.path} from user {userId}")
        if filterItemNames:
            itemNamesList = filterItemNames.split(",")
        else:
            itemNamesList = []
        orders: List[Order] = await getOrderHistoryQuery(
            db,
            userId,
            orderStatus,
            minOrderDate,
            maxOrderDate,
            minDeliveryDate,
            maxDeliveryDate,
            sortField,
            sortOrder,
            itemNamesList,
        )
        logger.debug(f"Request to {request.url.path} completed")
        return orders
    except Exception as e:
        logger.error(f"Request to {request.url.path} caused exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/cancel_order/{order_id}")
async def cancelOrder(
    request: Request,
    order_id: int,
    userId: Annotated[int, Depends(getUserIdFromName)],
    orderProcessor: Annotated[OrderProcessor, Depends(getOrderProcessor)],
):
    logger.debug(f"Request to {request.url.path} from user {userId}")
    try:
        await orderProcessor.cancelOrder(userId, order_id)
        logger.debug(f"Request to {request.url.path} completed")
    except ProcessOrderException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

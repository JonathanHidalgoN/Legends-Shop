from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import logger
from app.routes.auth import getUserIdFromName
from app.data import database
from app.cart.CartProcessor import CartProceesor
from app.customExceptions import CartProcessorException
from app.schemas.Order import CartItem

router = APIRouter()


def getCartProcessor(
    db: AsyncSession = Depends(database.getDbSession),
) -> CartProceesor:
    return CartProceesor(db)

@router.post("/add_items",response_model=List[CartItem])
async def addItems(
        request: Request,
        cartItems: List[CartItem],
    userId: Annotated[int, Depends(getUserIdFromName)],
    cartProcessor: Annotated[CartProceesor, Depends(getCartProcessor)],
):
    try:
        logger.debug(f"Request to {request.url.path} from user {userId}")
        processCart:List[CartItem] = await cartProcessor.addItemsToCar(cartItems, userId)
        logger.debug(f"Request to {request.url.path} from user {userId} completed")
        return  processCart
    except CartProcessorException as e:
        logger.error(f"Request to {request.url.path} caused exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/add_item",response_model=CartItem)
async def addItem(
        request: Request,
        cartItem: CartItem,
    userId: Annotated[int, Depends(getUserIdFromName)],
    cartProcessor: Annotated[CartProceesor, Depends(getCartProcessor)],
):
    try:
        logger.debug(f"Request to {request.url.path} from user {userId}")
        processCart:CartItem = await cartProcessor.addItemToCar(cartItem, userId)
        logger.debug(f"Request to {request.url.path} from user {userId} completed")
        return  processCart
    except CartProcessorException as e:
        logger.error(f"Request to {request.url.path} caused exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

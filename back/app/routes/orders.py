from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import checkItemExist, getGoldTableWithId, getItemTableGivenItemName
from app.logger import logger
from app.data import database
from app.routes.auth import getCurrentUserTokenFlow
from app.schemas.Order import Order

router = APIRouter()

async def checkIfOrderItemsAreValid(asyncSession: AsyncSession, itemNames:List[str]) -> bool:
    for itemName in itemNames:
        exist: bool = await checkItemExist(asyncSession, itemName)
        if not exist:
            raise Exception(f"Item with name {itemName} do not exist in the database")
    return True

@router.post("/order")
async def order(
    request: Request, 
    order: Order,
    userName: Annotated[str, Depends(getCurrentUserTokenFlow)],
    db: AsyncSession = Depends(database.getDbSession)
):
    try:
        logger.debug(f"Request to {request.url.path}")
        await checkIfOrderItemsAreValid(db, order.itemNames)
    except Exception as e:
        logger.error(f"Error in {request.url.path} {str(e)}")
        raise HTTPException(
            status_code=400, detail=str(e)
        )
    logger.debug(f"Request to {request.url.path} completed")
    return {"message": f"{order} {userName}"}

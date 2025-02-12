from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.utils import getAllItemTableRowsAnMapToItems
from app.logger import logger
from app.data import database
from app.schemas.Item import Item

router = APIRouter()


@router.get("/all")
async def getAllItems(db: AsyncSession = Depends(database.getDbSession)):
    items: List[Item] = []
    try:
        items = await getAllItemTableRowsAnMapToItems(db)
    except Exception as e:
        logger.error(f"Error while trying to query all items from database: {e}")
        raise HTTPException(
            status_code=500, detail="Error fetching items from the database"
        )
    return {"items": items}

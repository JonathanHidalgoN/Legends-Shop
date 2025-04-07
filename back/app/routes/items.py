from typing import List, Set
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.queries.itemQueries import (
    getAllEffectsTableName,
    getAllItemNames,
    getAllTagsTableNames,
)
from app.data.utils import (
    getAllItemTableRowsAnMapToItems,
    getSomeItemTableRowsAnMapToItems,
)
from app.logger import logger
from app.data import database
from app.schemas.Item import Item

router = APIRouter()


# TODO: Create a class to handle item fetching logic
@router.get("/all", response_model=List[Item])
async def getAllItems(
    request: Request, db: AsyncSession = Depends(database.getDbSession)
):
    items: List[Item] = []
    try:
        items = await getAllItemTableRowsAnMapToItems(db)
        return items
    except Exception as e:
        logger.error(
            f"Error while trying to query {request.url.path} from database: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Error fetching {request.url.path} the database"
        )


@router.get("/some", response_model=List[Item])
async def getSomeItems(
    request: Request, db: AsyncSession = Depends(database.getDbSession)
):
    items: List[Item] = []
    try:
        items = await getSomeItemTableRowsAnMapToItems(db)
        return items
    except Exception as e:
        logger.error(
            f"Error while trying to query {request.url.path} some items from database: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching {request.url.path} from the database",
        )


@router.get("/uniqueTags", response_model=List[str])
async def getUniqueTags(
    request: Request, db: AsyncSession = Depends(database.getDbSession)
):
    tagNames: Set[str] = set()
    try:
        tagNames = await getAllTagsTableNames(db)
        return list(tagNames)
    except Exception as e:
        logger.error(
            f"Error while trying to query {request.url.path} from database: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching {request.url.path} from the database",
        )


@router.get("/item_names", response_model=Set[str])
async def getItemNames(
    request: Request, db: AsyncSession = Depends(database.getDbSession)
):
    itemNames: Set[str] = set()
    try:
        itemNames = await getAllItemNames(db)
        return itemNames
    except Exception as e:
        logger.error(
            f"Error while trying to query {request.url.path} from database: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching {request.url.path} from the database",
        )


@router.get("/unique_effects", response_model=Set[str])
async def getUniqueEffects(
    request: Request, db: AsyncSession = Depends(database.getDbSession)
):
    effectNames: Set[str] = set()
    try:
        effectNames = await getAllEffectsTableName(db)
        return effectNames
    except Exception as e:
        logger.error(
            f"Error while trying to query {request.url.path} from database: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching {request.url.path} from the database",
        )

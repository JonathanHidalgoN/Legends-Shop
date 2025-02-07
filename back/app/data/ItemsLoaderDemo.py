from typing import List, Set
import json
import httpx

from pydantic import Json, ValidationError
from sqlalchemy import delete, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    ItemsLoaderError,
    JSONFetchError,
    JsonParseError,
    NoDataNodeInJSON,
    TableUpdateError,
    UpdateItemsError,
    UpdateStatsError,
    UpdateTagsError,
)
from app.data.mappers import mapGoldToGoldTable, mapItemToItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import ItemTagsAssociation, TagsTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import (
    getAllStatsTableNames,
    getAllTagsTableNames,
    getGoldTableWithItemId,
    getItemTableGivenName,
    getStatIdWithStatName,
    getTagIdWithtTagName,
)
from app.schemas.Item import Gold, Item, Stats
from app.logger import logger


class ItemsLoader:
    """
    This class is responsible to fetch the items from ITEMS_URL, then parse
    that json into a collection representing the items, with those items update the database.

    The only method to be used is 'updateItems', that method causes:
    """

    ITEMS_URL: str = (
        "https://ddragon.leagueoflegends.com/cdn/15.2.1/data/en_US/item.json"
    )

    def __init__(self, dbSession: AsyncSession):
        pass

    async def updateItems(self) -> None:
        """
        This method :
        1 - Get the json with items.
        2 - Parse the json with items into a list of items.
        3 - Update the tags table.
        4 - Update the stats table.
        5 - Update/insert the items in the database

        Raises ItemsLoaderError in the following flavors
        - JSONFetchError.
        - JsonParseError.
        - UpdateTagsError.
        - UpdateStatsError.
        - UpdateItemsError.
        """
        itemsJson: dict = await self.getItemsJson()
        if not itemsJson:
            logger.error("Items Json is empty")
            raise ItemsLoaderError("Items Json is empty!")
        itemsList: List[Item] = await self.parseItemsJsonIntoItemList(itemsJson)
        if not itemsList:
            logger.error("Items list is empty")
            raise ItemsLoaderError("Items Json is empty!")
        await self.updateTagsInDataBase()
        await self.updateStatsInDataBase()
        await self.updateItemsInDataBase(itemsList)

    async def getItemsJson(self) -> dict:
        """
        This method gets the json from ITEMS_URL and returns it.
        Raise a JSONFetchError when an error occurs
        """
        logger.debug("Getting json items")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ITEMS_URL)
                response.raise_for_status()
                data = response.json()
                logger.debug("Fetched json items successfully")
                return data
        except (json.JSONDecodeError, httpx.RequestError) as e:
            logger.exception(f"Error when fetching the JSON with items: {e}")
            raise JSONFetchError from e
        except Exception as e:
            logger.exception(
                f"Unexpected exception when fetching the JSON with items: {e}"
            )
            raise JSONFetchError from e

    async def parseItemsJsonIntoItemList(self, itemsJson: Json) -> List[Item]:
        itemsList: List[Item] = []
        return itemsList

    async def updateTagsInDataBase(self) -> None:
        pass

    async def updateStatsInDataBase(self) -> None:
        pass

    async def updateItemsInDataBase(self, itemsList: List[Item]) -> None:
        pass

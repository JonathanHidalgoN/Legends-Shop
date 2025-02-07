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
        self.dbSession = dbSession
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
        uniqueTags: Set[str] = set(tag for item in itemsList for tag in item.tags)
        await self.updateTagsInDataBase(uniqueTags)
        uniqueStats: Set[str] = set(
            stat for item in itemsList for stat in item.stats.root
        )
        await self.updateStatsInDataBase(uniqueStats)
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
        """
        Parses the json with items into a list of items.
        Raises JsonParseError if there is no 'data' node
        """
        logger.debug("Parsing json with items into a list of items")
        itemsList: List[Item] = []
        self.version = itemsJson.get("version")
        if self.version is None:
            logger.warning(
                "Error, itemsJson has no 'version' key, item parsing can continue"
            )
        itemsData: dict | None = itemsJson.get("data")
        if itemsData is None:
            logger.error("Error, the items JSON has no data node!")
            raise JsonParseError("Error, the items JSON has no data node!")
        itemNames : Set[str] = set() 
        noneCounter : int = 0
        parsedItems : int = 0
        for itemId, itemData in itemsData.items():
            item : Item | None = await self.parseDataNodeIntoItem(itemId, itemData, itemNames)
            if item is None:
                noneCounter +=1
            else:
                itemNames.add(item.name)
                itemsList.append(item)
                parsedItems += 1
        logger.debug(f"Parsed items Json successfully, with {parsedItems} parsed items and {noneCounter} items that could not be parsed")
        return itemsList

    async def parseDataNodeIntoItem(self,itemId: int, itemData, itemNames : Set[str]) -> Item | None:
        """
        Parses the 'data' node of the json with items into an Item.
        Raises nothing but if there is an error just will log a warning and ingore that item
        """
        if "name" not in itemData:
            logger.warning(
                f"Error, the item with id {itemId} has no 'name' node, item parsing will continue but this item won't be updated")
            return None
        try:
            if itemData["name"] in itemNames:
                logger.warning(
                    f"'name' node has the value {itemData["name"]} register multiple times, just one  (the first) will be register in the database")
                return None
            fullItem = {"id": itemId, **itemData}
            item: Item = Item(**fullItem)
            return item 
        except Exception as e:
            logger.error(
                f"Error, the item with id {itemId} had a problem while parsing the json into an Item, exception : {e}")
            return None

    async def updateTagsInDataBase(self, tagsToAdd:Set[str]) -> None:
        """
        Given a set of unique tags, iterate over them and update the tags table
        Raise UpdateTagsError 
        """
        logger.debug("Updating tags table")
        try:
            logger.debug("Getting existing gats in the database")
            existingTagNames: List[str] = await getAllTagsTableNames(self.dbSession)
            logger.debug(f"Got {len(existingTagNames)} from database")
        except SQLAlchemyError as e:
            logger.error(
                f"Error, could not get existing tag names in the database: {e}"
            )
            raise UpdateTagsError() from e
        logger.debug(f"Adding {len(tagsToAdd)} tags, just new tags will be added")
        newAditions : int = 0
        for tag in tagsToAdd:
            isNew : bool = await self.addTagInDataBaseIfNew(tag, existingTagNames)
            if isNew:
                newAditions +=1
        logger.debug(f"Updated tags table successfully, {newAditions} new tags added")

    async def addTagInDataBaseIfNew(self,tag:str, existingTagNames:List[str]) -> bool:
        """
        Updates the database with tag, if it do not exist.
        Raises UpdateTagsError
        """
        try:
            if tag not in existingTagNames:
                newTag: TagsTable = TagsTable(name=tag)
                self.dbSession.add(newTag)
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error while updating tag {tag}, exception: {e}")
            raise UpdateTagsError() from e


    async def updateStatsInDataBase(self, statsToAdd:Set[str]) -> None:
        """
        """
        pass

    async def updateItemsInDataBase(self, itemsList: List[Item]) -> None:
        """
        """
        pass

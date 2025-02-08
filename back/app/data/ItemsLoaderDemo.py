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
    getGoldIdWithItemId,
    getGoldTableWithItemId,
    getItemTableGivenItemName,
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
        #TODO: CHECK ASYNC
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
            existingTagNames: Set[str] = await getAllTagsTableNames(self.dbSession)
            logger.debug(f"Got {len(existingTagNames)} from database")
        except SQLAlchemyError as e:
            logger.error(
                f"Error, could not get existing tag names in the database: {e}"
            )
            raise UpdateTagsError() from e
        logger.debug(f"Adding {len(tagsToAdd)} tags, just new tags will be added")
        newAditions : int = 0
        for tag in tagsToAdd:
            isNew : bool = self.addTagInDataBaseIfNew(tag, existingTagNames)
            if isNew:
                newAditions +=1
        try:
            await self.dbSession.commit()
        except Exception as e:
            logger.error(f"An error occurred while commiting tags update: {e}")
            await self.dbSession.rollback()
            raise UpdateTagsError() from e
        logger.debug(f"Updated tags table successfully, {newAditions} new tags added")

    def addTagInDataBaseIfNew(self,tag:str, existingTagNames:Set[str]) -> bool:
        ##TODO: CAN THIS BE ASYNC AND THE LOOP STILL RUN?
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
        Given a set of unique stats, iterate over them and update the stats table
        Raise UpdateStatsError 
        """
        logger.debug("Updating stats table")
        try:
            logger.debug("Getting existing gats in the database")
            existingStatNames: Set[str] = await getAllStatsTableNames(self.dbSession)
            logger.debug(f"Got {len(existingStatNames)} from database")
        except SQLAlchemyError as e:
            logger.error(
                f"Error, could not get existing stat names in the database: {e}"
            )
            raise UpdateStatsError() from e
        logger.debug(f"Adding {len(statsToAdd)} stats, just new stats will be added")
        newAditions : int = 0
        for stat in statsToAdd:
            isNew : bool = self.addStatInDataBaseIfNew(stat, existingStatNames)
            if isNew:
                newAditions +=1
        try:
            await self.dbSession.commit()
        except Exception as e:
            logger.error(f"An error occurred while commiting stats update: {e}")
            await self.dbSession.rollback()
            raise UpdateStatsError() from e
        logger.debug(f"Updated stats table successfully, {newAditions} new stats added")

    def addStatInDataBaseIfNew(self,stat:str, existingstatNames:Set[str]) -> bool:
        ##TODO: CAN THIS BE ASYNC AND THE LOOP STILL RUN?
        """
        Updates the database with stat, if it do not exist.
        Raises UpdatestatsError
        """
        try:
            if stat not in existingstatNames:
                newStat: StatsTable = StatsTable(name=stat)
                self.dbSession.add(newStat)
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error while updating stat {stat}, exception: {e}")
            raise UpdateStatsError() from e


    async def updateItemsInDataBase(self, itemsList: List[Item]) -> None:
        """
        Updates the items in the database, transactions are added in a batch,
        if the insert/update fails then the transacion fails and changes are rollback.
        """
        logger.debug(f"Updating {len(itemsList)} items in the database")
        currentItemName : str = ""
        try:
            for item in itemsList:
                currentItemName = item.name
                existingItem : ItemTable | None = await getItemTableGivenItemName(self.dbSession,item.name)
                await self.insertOrUpdateItemTable(item,existingItem)
            await self.dbSession.commit()
            logger.debug(f"Updated {len(itemsList)} items successfully")
        except SQLAlchemyError as e:
            logger.debug(f"Error getting the item from the database with name {currentItemName}, exception: {e}")
            await self.dbSession.rollback()
            raise UpdateItemsError() from e
        except Exception as e:
            logger.debug(f"Error inserting/updating an item in the database with name {currentItemName}, exception: {e}")
            await self.dbSession.rollback()
            raise UpdateItemsError() from e

    async def insertOrUpdateItemTable(self, item: Item,existingItem : ItemTable | None)->None:
        """
        """
        goldTableId : int
        itemTable : ItemTable
        if existingItem is None:
            goldTableId = await self.insertOrUpdateGoldTable(True,item.gold,None)
            itemTable = mapItemToItemTable(item,goldTableId,True)
        else:
            await self.deleteItemStatsExistingRelations(existingItem.id)
            await self.deleteItemTagsExistingRelations(existingItem.id)
            goldTableId = await self.insertOrUpdateGoldTable(False,item.gold,existingItem.id)
            itemTable = existingItem
        try:
            await self.dbSession.merge(itemTable)
            await self.dbSession.flush()
        except Exception as e:
            logger.error("")
            raise UpdateItemsError() from e
       
    async def deleteItemTagsExistingRelations(self, itemId)-> None:
        pass

    async def deleteItemStatsExistingRelations(self, itemId)->None:
        pass

    async def insertOrUpdateGoldTable(self,createNewGoldTable:bool, gold:Gold, itemId:int | None = None)->int:
        """
        Insert or updates the gold table depending on the createNewGoldTable parameter
        Raises UpdateItemsError
        """
        if (itemId is None) and (createNewGoldTable is False):
            logger.error("Error trying to updating a gold table the item id can not be None")
            raise UpdateItemsError("Can not update a gold table with no item id")
        newGoldTable : GoldTable = mapGoldToGoldTable(gold)
        if (createNewGoldTable is False) and (itemId is not None):
            existingGoldTableId: int | None = await getGoldIdWithItemId(self.dbSession,itemId)
            if existingGoldTableId is None:
                logger.error(f"Error updating the row in gold table with item id {itemId}, did not find the row with goldId {existingGoldTableId}")
                raise UpdateItemsError("Tried to update a gold row that do not exist")
            newGoldTable.id = existingGoldTableId
        try:
            await self.dbSession.merge(newGoldTable)
            await self.dbSession.flush()
            return newGoldTable.id
        except Exception as e:
            logger.error(f"Error updating/inserting a gold table, exception: {e}")
            raise UpdateItemsError("Unexpected exception happened while inserting/updating a gold row") from e



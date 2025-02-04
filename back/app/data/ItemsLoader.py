from typing import List
import json
import httpx

from pydantic import Json, ValidationError
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    ItemsLoaderError,
    JSONFetchError,
    NoDataNodeInJSON,
    TableUpdateError,
)
from app.data.mappers import mapGoldToGoldTable, mapItemToItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import ItemTagsAssociation, TagsTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import (
    getAllStatsTable,
    getAllStatsTableNames,
    getAllTagsTableNames,
    getStatIdWithStatName,
    getTagIdWithtTagName,
)
from app.schemas.Item import Item, Stats
from app.logger import logger


class ItemsLoader:
    ITEMS_URL: str = (
        "https://ddragon.leagueoflegends.com/cdn/15.2.1/data/en_US/item.json"
    )

    def __init__(self, dbSession: AsyncSession, updated: bool = False):
        self.updated: bool = updated
        self.version: str | None = None
        self.dbSession = dbSession
        self.notUpdatedItemsId: List[int] = []

    async def getRawJson(self) -> dict | None:
        logger.debug("Getting json items")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ITEMS_URL)
                response.raise_for_status()
                data = response.json()
                logger.debug("Fetched json items successfully")
                return data
        except json.JSONDecodeError as e:
            logger.exception(f"JSON decode error when getting the items json : {e}")
            raise JSONFetchError("Invalid JSON received from API") from e
        except httpx.RequestError as e:
            logger.exception(f"HTTP request error when gettint the JSON items : {e}")
            raise JSONFetchError("HTTP error ocurred when fetching the items") from e
        except Exception as e:
            logger.exception(f"Exception when fetching the JSON with items : {e}")
            raise JSONFetchError(
            "An unexpected error ocurred when fetching JSON items"
            ) from e

    def parseRawJsonIntoItemsList(self, itemsDict: Json) -> List[Item]:
        logger.debug("Parsing json items into a list of items")
        items: List[Item] = []
        self.version = itemsDict.get("version")
        if self.version is None:
            logger.warning(
                "Error, itemsDict has no 'version' key, item parsing can continue"
            )
        itemsData: dict | None = itemsDict.get("data")
        if itemsData is None:
            errorStr: str = "Error, the items JSON has no data node!"
            logger.error(errorStr)
            self.updated = False
            raise NoDataNodeInJSON(errorStr)
        for itemId, itemData in itemsData.items():
            if "name" not in itemData:
                logger.error(
                    f"Error, the item with id {itemId} has no 'name' node, item parsing will continue but this item won't be updated"
                )
                self.notUpdatedItemsId.append(itemId)
                continue
            try:
                fullItem = {"id": itemId, **itemData}
                item: Item = Item(**fullItem)
                items.append(item)
            except ValidationError as e:
                self.notUpdatedItemsId.append(itemId)
                logger.exception(
                    f"Error, the item with id {itemId} could not be parsed, exception : {e}"
                )
        logger.debug(f"Parsed json items into a list with {len(items)}")
        return items

    async def updateItems(self) -> None:
        logger.debug("Updating items")
        itemsDict: dict | None = await self.getRawJson()
        if not itemsDict:
            raise ItemsLoaderError("Failed to fetch items JSON")
        itemsList: List[Item] = self.parseRawJsonIntoItemsList(itemsDict)
        if not itemsList:
            raise ItemsLoaderError("Error, items list is empty")
        succes: bool = await self.updateItemsTable(itemsList)
        if not succes:
            raise ItemsLoaderError("Failed to update items table")
        logger.debug("Updated items successfully")
        self.updated = True

    async def updateTagsTable(self, tagsList: List[str]) -> bool:
        try:
            existingTagNames: List[str] = await getAllTagsTableNames(self.dbSession)
            logger.debug(f"Updating tags table with {len(tagsList)} tags, just new tags will be added, currently {len(existingTagNames)} in the database")
            counter : int = 0
            for tag in tagsList:
                if tag not in existingTagNames:
                    newTag: TagsTable = TagsTable(name=tag)
                    self.dbSession.add(newTag)
                    existingTagNames.append(tag)
                    counter+=1
            await self.dbSession.commit()
            logger.debug(f"Updated tags table successfully, added {counter} new tags")
            return True
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(f"Error, could not update Tags table exception: {e}")
            raise TableUpdateError("Error updating tags table") from e

    async def updateStatsTable(self, statsList: List[str]) -> bool:
        try:
            existingStatNames: List[str] = await getAllStatsTableNames(self.dbSession)
            logger.debug(f"Updating stats table with {len(statsList)} stats, just new stats will be added, currently {len(existingStatNames)} in the database")
            counter : int = 0
            for stat in statsList:
                if stat not in statsList:
                    newStat: StatsTable = StatsTable(name=stat)
                    self.dbSession.add(newStat)
                    existingStatNames.append(stat)
                    counter+=1
            await self.dbSession.commit()
            logger.debug(f"Updated stats table successfully, added {counter} new stats")
            return True
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(f"Error, could not update Stats table exception: {e}")
            raise TableUpdateError("Error updating Stats table") from e

    async def _addStatsRelationWithItem(
        self, itemTable: ItemTable, stats: Stats
    ) -> None:
        try:
            for stat, statValue in stats.root.items():
                statId: int | None = await getStatIdWithStatName(self.dbSession, stat)
                if statId is None:
                    logger.error(
                        f"Error, an item has a stat that is not register in the database with name {stat}"
                    )
                    raise TableUpdateError(
                        "Item has a stat that is not in the database"
                    )
                itemStatValues: dict = {
                    "item_id": ItemTable.id,
                    "stat_id": statId,
                    "value": statValue,
                }
                ins = insert(ItemStatAssociation).values(**itemStatValues)
                await self.dbSession.execute(ins)
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(
                f"Could not link item with item id {itemTable.id} with stats table relation"
            )
            raise TableUpdateError(
                "Error creating relation between item and stats"
            ) from e

    async def _addTagsRelationWithItem(
        self, itemTable: ItemTable, tags: List[str]
    ) -> None:
        try:
            for tag in tags:
                tagId: int | None = await getTagIdWithtTagName(self.dbSession, tag)
                if tagId is None:
                    logger.error(
                        f"Error, an item has a tag that is not register in the database with name {tag}"
                    )
                    raise TableUpdateError("Item has a tag that is not in the database")
                itemtagsValues: dict = {
                    "item_id": ItemTable.id,
                    "tag_id": tagId,
                    "value": 0,
                }
                ins = insert(ItemTagsAssociation).values(**itemtagsValues)
                await self.dbSession.execute(ins)
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(
                f"Could not link item with item id {itemTable.id} with tags table relation"
            )
            raise TableUpdateError(
                "Error creating relation between item and tags"
            ) from e

    async def _updateItemInTable(self, item: Item) -> None:
        try:
            goldTable: GoldTable = mapGoldToGoldTable(item.gold)
            self.dbSession.add(goldTable)
            # Flush will update the id
            await self.dbSession.flush()
            goldId: int = goldTable.id
            itemTable: ItemTable = mapItemToItemTable(item, goldId, True)
            self.dbSession.add(itemTable)
            await self.dbSession.flush()
            await self._addStatsRelationWithItem(itemTable, item.stats)
            await self._addTagsRelationWithItem(itemTable, item.tags)
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(f"Error, could not update items table, exception: {e}")
            raise TableUpdateError("Error, could not update items table") from e

    async def updateItemsTable(self, itemsList: List[Item]) -> bool:
        try:
            logger.debug("Updating items table")
            tagsList: List[str] = [tag for item in itemsList for tag in item.tags]
            tagsUpdated: bool = await self.updateTagsTable(tagsList)
            statsList: List[str] = [
                stat for item in itemsList for stat in item.stats.root
            ]
            statsUpdated: bool = await self.updateStatsTable(statsList)
            if tagsUpdated and statsUpdated:
                for item in itemsList:
                    await self._updateItemInTable(item)
            logger.debug("Updated items table successfully")
            return True
        except TableUpdateError as e:
            self.updated = False
            raise e

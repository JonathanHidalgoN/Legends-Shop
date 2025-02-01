from typing import List
import json
import httpx

from pydantic import Json, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    ItemsLoaderError,
    JSONFetchError,
    NoDataNodeInJSON,
    TableUpdateError,
)
from app.data.mappers import mapGoldToGoldTable, mapItemToItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.StatsTable import StatsTable
from app.data.models.TagsTable import TagsTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import (
    getAllStatsTable,
    getAllStatsTableNames,
    getAllTagsTableNames,
)
from app.schemas.Item import Item
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
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ITEMS_URL)
                response.raise_for_status()
                data = response.json()
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
        return items

    async def updateItems(self) -> None:
        itemsDict: dict | None = await self.getRawJson()
        if not itemsDict:
            raise ItemsLoaderError("Failed to fetch items JSON")
        itemsList: List[Item] = self.parseRawJsonIntoItemsList(itemsDict)
        if not itemsList:
            raise ItemsLoaderError("Error, items list is empty")
        succes: bool = await self.updateItemsTable(itemsList)
        if not succes:
            raise ItemsLoaderError("Failed to update items table")
        self.updated = True

    async def updateTagsTable(self, tagsList: List[str]) -> bool:
        try:
            existingTagNames: List[str] = await getAllTagsTableNames(self.dbSession)
            for tag in tagsList:
                newTag: TagsTable = TagsTable(name=tag)
                self.dbSession.add(newTag)
                existingTagNames.append(tag)
            await self.dbSession.commit()
            return True
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(f"Error, could not update Tags table exception: {e}")
            raise TableUpdateError("Error updating tags table") from e

    async def updateStatsTable(self, statsList: List[str]) -> bool:
        try:
            existingStatNames: List[str] = await getAllStatsTableNames(self.dbSession)
            for stat in statsList:
                newStat: StatsTable = StatsTable(name=stat)
                self.dbSession.add(newStat)
                existingStatNames.append(stat)
            await self.dbSession.commit()
            return True
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(f"Error, could not update Stats table exception: {e}")
            raise TableUpdateError("Error updating Stats table") from e

    async def _updateItemInTable(self, item: Item) -> None:
        # goldTable: GoldTable = mapGoldToGoldTable(item.gold)
        # itemTable: ItemTable = mapItemToItemTable(item, 0, True)
        return None

    async def updateItemsTable(self, itemsList: List[Item]) -> bool:
        try:
            tagsList: List[str] = [tag for item in itemsList for tag in item.tags]
            tagsUpdated: bool = await self.updateTagsTable(tagsList)
            statsList: List[str] = [
                stat for item in itemsList for stat in item.stats.root
            ]
            statsUpdated: bool = await self.updateStatsTable(statsList)
            if tagsUpdated and statsUpdated:
                for item in itemsList:
                    await self._updateItemInTable(item)
            return True
        except TableUpdateError as e:
            self.updated = False
            raise e

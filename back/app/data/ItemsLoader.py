from typing import List
import json
import httpx

from pydantic import Json, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.models.TagsTable import TagsTable
from app.data.queries.itemQueries import getAllTagsTableNames
from app.schemas.Item import Item


class ItemsLoader:
    ITEMS_URL: str = (
        "https://ddragon.leagueoflegends.com/cdn/15.2.1/data/en_US/item.json"
    )

    def __init__(self, dbSession: AsyncSession, updated: bool = False):
        self.updated: bool = updated
        self.version: str | None = None
        self.dbSession = dbSession
        self.notUpdatedItemsId: List[int] = []

    # This method gets the raw json from the API and updates a flag
    # if no errors
    async def getRawJson(self) -> dict | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ITEMS_URL)
                response.raise_for_status()
                data = response.json()
                return data
        except json.JSONDecodeError as e:
            self.updated = False
            print(f"JSON Decode Error getting the items json: {e.msg}")
        except httpx.RequestError as e:
            self.updated = False
            print(f"An error occurred during the HTTP request: {e}")
        except Exception as e:
            self.updated = False
            print(f"An error occurred getting the items json: {e}")
        return None

    # This method parse the items from the json validating with a pydantic scheme
    def parseRawJsonIntoItemsList(self, itemsDict: Json) -> List[Item]:
        items: List[Item] = []
        if "version" in itemsDict:
            self.version = itemsDict["version"]
        else:
            self.version = None
            print("Error, itemsDict has no version node")
        currentKey = "data"
        if "data" in itemsDict:
            itemsData: dict = itemsDict[currentKey]
            for itemId, itemData in itemsData.items():
                currentKey = "name"
                if currentKey in itemData:
                    try:
                        fullItem: dict = {"id": itemId, **itemData}
                        item: Item = Item(**fullItem)
                        items.append(item)
                    except ValidationError as e:
                        self.notUpdatedItemsId.append(itemId)
                        print(f"Error parsing item {itemId}: {e}")
                else:
                    print(f"Error parsing an item {itemId} with no {currentKey} node")
                    self.notUpdatedItemsId.append(itemId)
        else:
            self.updated = False
            print("Error: items json has no data node")
        return items

    def updateTable(self, itemsList: List[Item]):
        pass

    async def updateTagsTable(self, tagsList: List[str]):
        existingTagNames: List[str] = await getAllTagsTableNames(self.dbSession)
        for tagName in tagsList:
            if tagName not in existingTagNames:
                newTag: TagsTable = TagsTable(name=tagName)
                self.dbSession.add(newTag)
                existingTagNames.append(newTag)

        await self.dbSession.commit()

    async def updateItems(self):
        itemsDict: dict | None = await self.getRawJson()
        if itemsDict:
            itemsList: List[Item] = self.parseRawJsonIntoItemsList(itemsDict)
            if not itemsList:
                self.updated = False
                print("Error in items list, it is empy")
            return itemsList

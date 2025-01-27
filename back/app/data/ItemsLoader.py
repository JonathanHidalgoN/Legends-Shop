from typing import List
import urllib.request
import json

from pydantic import ValidationError
from schemas.Item import Item


class ItemsLoader:
    ITEMS_URL: str = (
        "https://ddragon.leagueoflegends.com/cdn/15.2.1/data/en_US/item.json"
    )

    def __init__(self, updated: bool = False):
        self.updated: bool = updated
        self.version: str | None = None
        self.notUpdatedItemsId: List[int] = []

    # This method gets the raw json from the API and updates a flag
    # if no errors
    def getRawJson(self) -> dict | None:
        try:
            response = urllib.request.urlopen(self.ITEMS_URL)
            data = json.loads(response.read().decode())
            return data
        except json.JSONDecodeError as e:
            self.updated = False
            print(f"JSON Decode Error getting the items json: {e.msg}")
        except Exception as e:
            self.updated = False
            print(f"An error occurred getting the items json: {e}")
        return None

    # This method parse the items from the json validating with a pydantic scheme
    def parseRawJsonIntoItemsList(self, itemsDict: dict) -> List[Item]:
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
                        item: Item = Item(**itemData)
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

    def updateItems(self):
        itemsDict: dict | None = self.getRawJson()
        if itemsDict:
            itemsList: List[Item] = self.parseRawJsonIntoItemsList(itemsDict)
            if not itemsList:
                self.updated = False
                print("Error in items list, it is empy")
            return itemsList

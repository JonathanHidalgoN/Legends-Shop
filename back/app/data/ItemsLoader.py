from typing import Dict, List, Set
import json
import httpx

from pydantic import Json
from sqlalchemy import delete, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.customExceptions import (
    ItemsLoaderError,
    JsonFetchError,
    JsonParseError,
    UpdateEffectsError,
    UpdateItemsError,
    UpdateStatsError,
    UpdateTagsError,
)
from app.data.mappers import mapGoldToGoldTable, mapItemToItemTable
from app.data.models.EffectsTable import EffectsTable, ItemEffectAssociation
from app.data.models.GoldTable import GoldTable
from app.data.models.StatsMappingTable import StatsMappingTable
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import ItemTagsAssociation, TagsTable
from app.data.models.ItemTable import ItemTable
from app.data.queries.itemQueries import (
    getAllEffectsTableNames,
    getAllStatsTableNames,
    getAllTagsTableNames,
    getEffectIdWithEffectName,
    getGoldIdWithItemId,
    getItemTableGivenItemName,
    getStatIdWithStatName,
    getStatsMappingTable,
    getTagIdWithtTagName,
    getVersion,
    insertVersion,
    updateVersion,
)
from app.schemas.Item import Effects, Gold, Item, Stat
from app.logger import logger
from app.logger import logMethod
from app.items.defaultItems import DEFAULT_ITEMS


# TODO: remove commits just one needed
class ItemsLoader:
    """
    Handles fetching, parsing, and updating item data from the League of Legends API.

    This class fetches item data from the `ITEMS_URL`, parses the JSON into item objects,
    and updates the database accordingly.

    The main method to be used is `updateItems()`.
    """
    VERSION_URL: str = "https://ddragon.leagueoflegends.com/api/versions.json"

    def __init__(self, dbSession: AsyncSession, filter:List[str] = DEFAULT_ITEMS):
        self.dbSession = dbSession
        self.version: str = ""
        self.itemsUrl: str = ""
        self.selectedItems: List[str] = filter

    @logMethod
    async def getJson(self, url: str) -> dict | list:
        """
        Fetches JSON data from the provided URL.

        Args:
            url (str): The URL from which to fetch the JSON data.
            entitiesName (str): The name of the entities being fetched (used for logging).

        Returns:
            dict | list: The fetched JSON data.

        Raises:
            JsonFetchError: If an error occurs while fetching or parsing the JSON.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data
        except (json.JSONDecodeError, httpx.RequestError) as e:
            raise JsonFetchError from e
        except Exception as e:
            raise JsonFetchError from e

    @logMethod
    async def getLastVersion(self) -> str:
        """
        Retrieves the latest version of the game from the version list.

        Returns:
            str: The latest game version.

        Raises:
            JsonParseError: If the version list is empty or if fetching the JSON fails.
        """
        # This is a list, use union to avoid typing error
        versionJson: list | dict = await self.getJson(self.VERSION_URL)
        if not versionJson:
            raise JsonParseError("Version json is empty")
        return versionJson[0]

    @logMethod
    def makeItemsUlr(self, version: str) -> str:
        """
        Constructs the item data URL based on the provided game version.

        Args:
            version (str): The game version to construct the URL for.

        Returns:
            str: The constructed item data URL.
        """
        itemsUrl: str = (
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
        )
        return itemsUrl

    @logMethod
    async def updateItems(self) -> None:
        if len(self.selectedItems) == 0:
            logger.info("No items in selected items, returning...")
            return
        currentVersion: str | None = await getVersion(self.dbSession)
        lastVersion: str = await self.getLastVersion()
        if currentVersion == lastVersion:
            return
        self.version = lastVersion
        await self.updateItemsStepsJob()
        if currentVersion is None:
            await insertVersion(self.dbSession, lastVersion)
        elif currentVersion != lastVersion:
            await self.updateDbVersion(lastVersion)

    @logMethod
    async def updateItemsStepsJob(self) -> None:
        """
        Updates the database with the latest game items.

        This method performs the following steps:
        - Builds the item data URL.
        - Fetches item JSON data.
        - Parses item JSON data into a list of item objects.
        - Updates the tags, stats, and effects tables.
        - Inserts or updates items in the database.

        Raises:
            ItemsLoaderError: If any error occurs during the update process.
        """
        self.itemsUrl = self.makeItemsUlr(self.version)
        itemsJson: dict | list = await self.getJson(self.itemsUrl)
        if not itemsJson:
            raise ItemsLoaderError("Items Json is empty!")
        itemsList: List[Item] = await self.parseItemsJsonIntoItemList(itemsJson)
        if not itemsList:
            raise ItemsLoaderError("Items Json is empty!")
        # Here again linter gives an error but the pidantic default constructor is an empty container
        # not none, I think this will be fine
        uniqueTags: Set[str] = set(tag for item in itemsList for tag in item.tags)
        await self.updateTagsInDataBase(uniqueTags)
        uniqueStats: Set[Stat] = self.getUniqueStats(itemsList)
        await self.updateStatsInDataBase(uniqueStats)
        # TODO: we dont like nested loops in python ):
        uniqueEffects: Set[str] = set(
            effect for item in itemsList for effect in item.effect.root
        )
        await self.updateEffectsInDataBase(uniqueEffects)
        await self.updateItemsInDataBase(itemsList)

    @logMethod
    def getUniqueStats(self, items: List[Item]) -> Set[Stat]:
        # I dont like this function because the stats are store as a catalog in the database,
        # the objective of this function is to get the unique stats in the list of items to update that catalog
        # The thing is that Stat object has a value attribute, so we have to check if stat is unique just by its name
        """
        Extracts unique stats from the given list of items.

        This function ensures uniqueness by checking only the stat name and kind.

        Args:
            items (List[Item]): The list of items containing stats.

        Returns:
            Set[Stat]: A set of unique stats.
        """
        uniqueStats: Set[Stat] = set()
        # TODO: we dont like nested loops in python ):
        for item in items:
            for stat in item.stats:
                # Have to get the list of names
                if stat.name not in [stat.name for stat in uniqueStats]:
                    uniqueStats.add(stat)
        return uniqueStats

    @logMethod
    async def updateDbVersion(self, version: str) -> None:
        """
        Updates the metadata version in the database.

        Args:
            version (str): The game version to store in the metadata.

        Raises:
            ItemsLoaderError: If updating the version fails.
        """
        try:
            await updateVersion(self.dbSession, version)
        except Exception as e:
            await self.dbSession.rollback()
            raise ItemsLoaderError() from e

    @logMethod
    async def parseItemsJsonIntoItemList(self, itemsJson: Json) -> List[Item]:
        """
        Parses the json with items into a list of items.
        Raises JsonParseError if there is no 'data' node
        """
        itemsList: List[Item] = []
        itemsData: dict | None = itemsJson.get("data")
        if itemsData is None:
            raise JsonParseError("Error, the items JSON has no data node!")
        itemNames: Set[str] = set()
        noneCounter: int = 0
        parsedItems: int = 0
        mappingStatsDict: Dict[str, str] = self.createMappingStatsDict(
            (await getStatsMappingTable(self.dbSession))
        )
        for itemId, itemData in itemsData.items():
            item: Item | None = await self.parseDataNodeIntoItem(
                itemId, itemData, itemNames, mappingStatsDict
            )
            if item is None:
                noneCounter += 1
            else:
                itemNames.add(item.name)
                itemsList.append(item)
                parsedItems += 1
        return itemsList

    # This could be static but for now its ok
    @logMethod
    def createMappingStatsDict(
        self, statsMappingTable: List[StatsMappingTable]
    ) -> Dict[str, str]:
        """
        Create a dict to map stats names from riot api to "better names"(IMO) using a table in the database
        called StatsMappingTable, it just has two rows one with the riot stat name and another with the custom name
        """
        mapping: Dict[str, str] = {}
        for row in statsMappingTable:
            mapping[row.original_name] = row.mapped_name
        return mapping

    @logMethod
    async def parseDataNodeIntoItem(
        self, itemId: int, itemData, itemNames: Set[str], statMapping: Dict[str, str]
    ) -> Item | None:
        # TODO: CHECK ASYNC
        """
        Parses the 'data' node of the json with items into an Item.
        Raises nothing but if there is an error just will log a warning and ingore that item
        """
        if "name" not in itemData:
            logger.warning(
                f"Error, the item with id {itemId} has no 'name' node, item parsing will continue but this item won't be updated"
            )
            return None
        try:
            if itemData["name"] in itemNames:
                logger.warning(
                    f"'name' node has the value {itemData['name']} register multiple times, just one (the first) will be register in the database"
                )
                return None
            if itemData["name"] not in self.selectedItems:
                return None
            return Item(
                name=itemData["name"],
                id=itemId,
                plaintext=itemData["plaintext"],
                image=itemData["image"]["full"],
                imageUrl=self.buildImageUrl(itemData["image"]["full"]),
                gold=(
                    Gold(**itemData["gold"])
                    if "gold" in itemData
                    else Gold(base=0, purchasable=False, total=0, sell=0)
                ),
                tags=set(itemData["tags"]) if "tags" in itemData else set(),
                stats=(
                    self.parseStatsNodeIntoStats(itemData["stats"], statMapping)
                    if "stats" in itemData
                    else set()
                ),
                description=itemData["description"],
                effect=(
                    Effects(root=itemData["effect"])
                    if "effect" in itemData
                    else Effects(root={})
                ),
            )
        except Exception as e:
            logger.warning(
                f"Error, the item with id {itemId} item parsing will continue but this item won't be updated, exception {e}"
            )
            return None

    @logMethod
    def parseStatsNodeIntoStats(
        self, statsNode: Dict[str, int | float], statMappingDict: Dict[str, str]
    ) -> Set[Stat]:
        """
        Parse the stat node into a stat list
        Raises nothing
        """
        stats: Set[Stat] = set()
        for statOriginalName, statValue in statsNode.items():
            statKind: str = "flat"
            if "Flat" not in statOriginalName or "Percent" not in statOriginalName:
                logger.warning(
                    f"Stat mapping error, stat with original name {statOriginalName} has no flat or percent in the name, cant decide the kind of stat, default is flat"
                )
            if "Percent" in statOriginalName:
                statKind = "percentage"
            statMappedName: str = statOriginalName
            if statOriginalName in statMappingDict:
                statMappedName = statMappingDict[statOriginalName]
            stat: Stat = Stat(name=statMappedName, value=statValue, kind=statKind)
            stats.add(stat)
        return stats

    @logMethod
    def buildImageUrl(self, imageName: str) -> str:
        """
        Build the image url given the version and image name
        """
        return f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/item/{imageName}"

    @logMethod
    async def updateTagsInDataBase(self, tagsToAdd: Set[str]) -> None:
        """
        Updates the tags table by adding new unique tags.

        Args:
            tagsToAdd (Set[str]): The set of unique tags to be added.

        Raises:
            UpdateTagsError: If fetching or updating tags fails.
        """
        try:
            existingTagNames: Set[str] = await getAllTagsTableNames(self.dbSession)
        except Exception as e:
            raise UpdateTagsError() from e
        newAditions: int = 0
        for tag in tagsToAdd:
            isNew: bool = self.addTagInDataBaseIfNew(tag, existingTagNames)
            if isNew:
                newAditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            await self.dbSession.rollback()
            raise UpdateTagsError() from e

    @logMethod
    def addTagInDataBaseIfNew(self, tag: str, existingTagNames: Set[str]) -> bool:
        ##TODO: CAN THIS BE ASYNC AND THE LOOP STILL RUN?
        """
        Adds a tag to the database if it does not already exist.

        Args:
            tag (str): The tag to be added.
            existingTagNames (Set[str]): The set of existing tag names.

        Returns:
            bool: True if the tag was added, False if it already existed.

        Raises:
            UpdateTagsError: If an error occurs while adding the tag.
        """
        try:
            if tag not in existingTagNames:
                newTag: TagsTable = TagsTable(name=tag)
                self.dbSession.add(newTag)
                return True
            else:
                return False
        except Exception as e:
            raise UpdateTagsError() from e

    @logMethod
    async def updateStatsInDataBase(self, statsToAdd: Set[Stat]) -> None:
        """
        Given a set of unique stats, iterate over them and update the stats table
        Raise UpdateStatsError
        """
        try:
            existingStatNames: Set[str] = await getAllStatsTableNames(self.dbSession)
        except SQLAlchemyError as e:
            raise UpdateStatsError() from e
        newAditions: int = 0
        for stat in statsToAdd:
            isNew: bool = self.addStatInDataBaseIfNew(stat, existingStatNames)
            if isNew:
                newAditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            await self.dbSession.rollback()
            raise UpdateStatsError() from e

    @logMethod
    async def updateEffectsInDataBase(self, effectsToAdd: Set[str]) -> None:
        """
        Given a set of unique effects, iterate over them and update the effects table.
        Raises UpdateEffectsError.
        """
        try:
            existingEffectNames: Set[str] = await getAllEffectsTableNames(
                self.dbSession
            )
        except SQLAlchemyError as e:
            raise UpdateEffectsError() from e

        newAdditions: int = 0
        for effect in effectsToAdd:
            isNew: bool = self.addEffectInDataBaseIfNew(effect, existingEffectNames)
            if isNew:
                newAdditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            await self.dbSession.rollback()
            raise UpdateEffectsError() from e

    @logMethod
    def addEffectInDataBaseIfNew(
        self, effect: str, existingEffectNames: Set[str]
    ) -> bool:
        ##TODO: CAN THIS BE ASYNC AND THE LOOP STILL RUN?
        """
        Updates the database with effect, if it does not exist.
        Raises UpdateEffectsError.
        """
        try:
            if effect not in existingEffectNames:
                newEffect: EffectsTable = EffectsTable(name=effect)
                self.dbSession.add(newEffect)
                return True
            else:
                return False
        except Exception as e:
            raise UpdateEffectsError() from e

    @logMethod
    def addStatInDataBaseIfNew(self, stat: Stat, existingstatNames: Set[str]) -> bool:
        ##TODO: CAN THIS BE ASYNC AND THE LOOP STILL RUN?
        """
        Updates the database with stat, if it do not exist.
        Raises UpdatestatsError
        """
        try:
            if stat.name not in existingstatNames:
                newStat: StatsTable = StatsTable(name=stat.name, kind=stat.kind)
                self.dbSession.add(newStat)
                return True
            else:
                return False
        except Exception as e:
            raise UpdateStatsError() from e

    @logMethod
    async def updateItemsInDataBase(self, itemsList: List[Item]) -> None:
        """
        Updates the items in the database, transactions are added in a batch,
        if the insert/update fails then the transacion fails and changes are rollback.
        """
        try:
            for item in itemsList:
                existingItem: ItemTable | None = await getItemTableGivenItemName(
                    self.dbSession, item.name
                )
                await self.insertOrUpdateItemTable(item, existingItem)
            await self.dbSession.commit()
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise UpdateItemsError() from e
        except Exception as e:
            await self.dbSession.rollback()
            raise UpdateItemsError() from e

    @logMethod
    async def insertOrUpdateItemTable(
        self, item: Item, existingItem: ItemTable | None
    ) -> None:
        """
        This function insert or updates the item depending if existingItem is None or itemTable
        Steps
        1 - Creates/updates and flush a gold table
        2 - Do nothing if its new or deletes existing tags and stats relations with the item if exist
        3 - Creates a new itemTable and if exist assing the existingItem id to the new item
        4 - Inserts/updates the new row
        5 - Add many to many stats and tags relations
        """
        goldTableId: int
        itemTable: ItemTable
        if existingItem is None:
            goldTableId = await self.insertOrUpdateGoldTable(True, item.gold, None)
            itemTable = mapItemToItemTable(item, goldTableId, True)
        else:
            await self.deleteItemStatsExistingRelations(existingItem.id)
            await self.deleteItemEffectsExistingRelations(existingItem.id)
            await self.deleteItemTagsExistingRelations(existingItem.id)
            goldTableId = await self.insertOrUpdateGoldTable(
                False, item.gold, existingItem.id
            )
            itemTable = mapItemToItemTable(item, goldTableId, True)
            itemTable.id = existingItem.id
        try:
            itemTable = await self.dbSession.merge(itemTable)
            await self.dbSession.flush()
            # Here the linter gives an error because stats, effects or tags can be None but in reality
            # the default constructor is empty so I think its fine
            await self.addItemStatsRelations(itemTable.id, item.stats)
            await self.addItemEffectsRelations(itemTable.id, item.effect)
            await self.addItemTagsRelations(itemTable.id, item.tags)
        except UpdateItemsError as e:
            raise e
        except Exception as e:
            raise UpdateItemsError() from e

    @logMethod
    async def addItemStatsRelations(self, itemId: int, stats: Set[Stat]) -> None:
        """
        This function inserts the relations given the itemId and stats
        Raises UpdateItemsError when something fails
        """
        for stat in stats:
            statId: int | None = await getStatIdWithStatName(self.dbSession, stat.name)
            if statId is None:
                raise UpdateItemsError("Stat was not found in the database")
            else:
                itemStatValues: dict = {
                    "item_id": itemId,
                    "stat_id": statId,
                    "value": stat.value,
                }
                try:
                    ins = insert(ItemStatAssociation).values(**itemStatValues)
                    await self.dbSession.execute(ins)
                except Exception as e:
                    raise UpdateItemsError(
                        "Could not insert a relation item-stat"
                    ) from e

    @logMethod
    async def addItemEffectsRelations(self, itemId: int, effects: Effects) -> None:
        """
        This function inserts the relations given the itemId and effects.
        Raises UpdateItemsError when something fails.
        """
        for effect, effectValue in effects.root.items():
            effectId: int | None = await getEffectIdWithEffectName(
                self.dbSession, effect
            )
            if effectId is None:
                raise UpdateItemsError("Effect was not found in the database")
            else:
                itemEffectValues: dict = {
                    "item_id": itemId,
                    "effect_id": effectId,
                    "value": effectValue,
                }
                try:
                    ins = insert(ItemEffectAssociation).values(**itemEffectValues)
                    await self.dbSession.execute(ins)
                except Exception as e:
                    raise UpdateItemsError(
                        "Could not insert a relation item-effect"
                    ) from e

    @logMethod
    async def addItemTagsRelations(self, itemId: int, tags: Set[str]) -> None:
        """
        This function inserts the relations given the itemId and tags
        Raises UpdateItemsError when something fails
        """
        for tag in tags:
            tagId: int | None = await getTagIdWithtTagName(self.dbSession, tag)
            if tagId is None:
                raise UpdateItemsError("Tag was not found in the database")
            itemtagsValues: dict = {"item_id": itemId, "tags_id": tagId}
            try:
                ins = insert(ItemTagsAssociation).values(**itemtagsValues)
                await self.dbSession.execute(ins)
            except Exception as e:
                raise UpdateItemsError("Could not insert a relation item-tag") from e

    @logMethod
    async def deleteItemTagsExistingRelations(self, itemId) -> None:
        """
        This function deletes the many to many relation of an item with
        the tags table
        Raises UpdateItemsError when something fails
        """
        delInstruction = delete(ItemTagsAssociation).where(
            ItemTagsAssociation.c.item_id == itemId
        )
        try:
            await self.dbSession.execute(delInstruction)
        except Exception as e:
            raise UpdateItemsError("Error while deleting tags associations for item")

    @logMethod
    async def deleteItemStatsExistingRelations(self, itemId) -> None:
        """
        This function deletes the many to many relation of an item with
        the stats table
        Raises UpdateItemsError when something fails
        """
        delInstruction = delete(ItemStatAssociation).where(
            ItemStatAssociation.c.item_id == itemId
        )
        try:
            await self.dbSession.execute(delInstruction)
        except Exception as e:
            raise UpdateItemsError("Error while deleting stats associations for item")

    @logMethod
    async def deleteItemEffectsExistingRelations(self, itemId) -> None:
        """
        This function deletes the many-to-many relation of an item with
        the effects table.
        Raises UpdateItemsError when something fails.
        """
        delInstruction = delete(ItemEffectAssociation).where(
            ItemEffectAssociation.c.item_id == itemId
        )
        try:
            await self.dbSession.execute(delInstruction)
        except Exception as e:
            raise UpdateItemsError("Error while deleting effects associations for item")

    @logMethod
    async def insertOrUpdateGoldTable(
        self, createNewGoldTable: bool, gold: Gold, itemId: int | None = None
    ) -> int:
        """
        Insert or updates the gold table depending on the createNewGoldTable parameter
        Raises UpdateItemsError
        """
        if (itemId is None) and (createNewGoldTable is False):
            raise UpdateItemsError("Can not update a gold table with no item id")
        newGoldTable: GoldTable = mapGoldToGoldTable(gold)
        if (createNewGoldTable is False) and (itemId is not None):
            existingGoldTableId: int | None = await getGoldIdWithItemId(
                self.dbSession, itemId
            )
            if existingGoldTableId is None:
                raise UpdateItemsError("Tried to update a gold row that do not exist")
            newGoldTable.id = existingGoldTableId
        try:
            newGoldTable = await self.dbSession.merge(newGoldTable)
            await self.dbSession.flush()
            return newGoldTable.id
        except Exception as e:
            raise UpdateItemsError(
                "Unexpected exception happened while inserting/updating a gold row"
            ) from e

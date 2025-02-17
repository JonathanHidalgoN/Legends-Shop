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
    updateVersion,
)
from app.schemas.Item import Effects, Gold, Item, Stat
from app.logger import logger


class ItemsLoader:
    # I know this class has a lot of code duplication where stats/effects are involved,
    # maybe is worth to abastract but for now I decided to create indivial functions because
    # in the future some different functionality will be added
    """
    This class is responsible to fetch the items from ITEMS_URL, then parse
    that json into a collection representing the items, with those items update the database.

    The only method to be used is 'updateItems'
    """
    VERSION_URL: str = "https://ddragon.leagueoflegends.com/api/versions.json"

    def __init__(self, dbSession: AsyncSession):
        self.dbSession = dbSession
        self.items_url: str = ""
        self.version: str = ""
        self.itemsUrl: str = ""

    async def getJson(self, url: str, entitiesName: str) -> dict | list:
        """
        This method gets the json from url and returns it.
        Raise a JSONFetchError when an error occurs
        """
        logger.debug(f"Getting {entitiesName} json in {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                logger.debug("Fetched json successfully")
                return data
        except (json.JSONDecodeError, httpx.RequestError) as e:
            logger.exception(
                f"Json decode error fetching {entitiesName} json in {url}, exception: {e}"
            )
            raise JsonFetchError from e
        except Exception as e:
            logger.exception(
                f"Unexpected exception fetching {entitiesName} json in {url}, exception: {e}"
            )
            raise JsonFetchError from e

    async def getLastVersion(self) -> str:
        """
        This functions gets the version list from VERSION_URL and get the first element that is the last version
        Raises JsonParseError when the version list is empty or exceptions raised by getJson method
        """
        # This is a list, use union to avoid typing error
        logger.debug("Getting current game version")
        versionJson: list | dict = await self.getJson(self.VERSION_URL, "versions")
        if not versionJson:
            logger.error("Version json is empty")
            raise JsonParseError("Version json is empty")
        logger.debug(f"Current game version is {versionJson[0]}")
        return versionJson[0]

    def makeItemsUlr(self, version: str) -> str:
        """
        Makes the items url with the current version of the game
        """
        logger.debug("Making items url")
        itemsUrl: str = (
            f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
        )
        logger.debug(f"Items url is {itemsUrl}")
        return itemsUrl

    async def updateItems(self) -> None:
        """
        This method :
        -2 - Gets the last version of the game and store
        -1 - Updates metadata version in database
        0 - Builds the items url and store
        1 - Gets the json with items.
        2 - Parses the json with items into a list of items.
        3 - Updates the tags table.
        4 - Updates the stats table.
        5 - Updates the effects table.
        6 - Updates/inserts the items in the database

        Raises ItemsLoaderError in the following flavors
        - JSONFetchError.
        - JsonParseError.
        - UpdateTagsError.
        - UpdateStatsError.
        - UpdateItemsError.
        - UpdateEffectsError.
        """
        self.version = await self.getLastVersion()
        await self.updateDbVersion(self.version)
        self.itemsUrl = self.makeItemsUlr(self.version)
        itemsJson: dict | list = await self.getJson(self.itemsUrl, "items")
        if not itemsJson:
            logger.error("Items Json is empty")
            raise ItemsLoaderError("Items Json is empty!")
        itemsList: List[Item] = await self.parseItemsJsonIntoItemList(itemsJson)
        if not itemsList:
            logger.error("Items list is empty")
            raise ItemsLoaderError("Items Json is empty!")
        #Here again linter gives an error but the pidantic default constructor is an empty container 
        #not none, I think this will be fine
        uniqueTags: Set[str] = set(tag for item in itemsList for tag in item.tags)
        await self.updateTagsInDataBase(uniqueTags)
        uniqueStats: Set[Stat] = self.getUniqueStats(itemsList) 
        await self.updateStatsInDataBase(uniqueStats)
        #TODO: we dont like nested loops in python ):
        uniqueEffects: Set[str] = set(
            effect for item in itemsList for effect in item.effect.root
        )
        await self.updateEffectsInDataBase(uniqueEffects)
        await self.updateItemsInDataBase(itemsList)

    def getUniqueStats(self, items: List[Item]) -> Set[Stat]:
        #I dont like this function because the stats are store as a catalog in the database,
        #the objective of this function is to get the unique stats in the list of items to update that catalog
        #The thing is that Stat object has a value attribute, so we have to check if stat is unique just by its name 
        """
        Given a list of items returns a list of unique stats, we only care about the name and kind
        """
        uniqueStats : Set[Stat] = set() 
        #TODO: we dont like nested loops in python ):
        for item in items:
            for stat in item.stats:
                #Have to get the list of names
                if stat.name not in [stat.name for stat in uniqueStats]:
                    uniqueStats.add(stat)
        return uniqueStats

    async def updateDbVersion(self, version: str) -> None:
        """
        Updates version in MetaDataTable
        Raises JsonParseError if version is None or error
        """
        try:
            await updateVersion(self.dbSession, version)
        except Exception as e:
            await self.dbSession.rollback()
            logger.error(
                f"An error occurred while updating the version in MetaDataTable, exception: {e}"
            )
            raise JsonParseError() from e

    async def parseItemsJsonIntoItemList(self, itemsJson: Json) -> List[Item]:
        """
        Parses the json with items into a list of items.
        Raises JsonParseError if there is no 'data' node
        """
        logger.debug("Parsing json with items into a list of items")
        itemsList: List[Item] = []
        await self.updateDbVersion(itemsJson.get("version"))
        itemsData: dict | None = itemsJson.get("data")
        if itemsData is None:
            logger.error("Error, the items JSON has no data node!")
            raise JsonParseError("Error, the items JSON has no data node!")
        itemNames: Set[str] = set()
        noneCounter: int = 0
        parsedItems: int = 0
        mappingStatsDict : Dict[str, str] = self.createMappingStatsDict((
            await getStatsMappingTable(self.dbSession)
        ))
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
        logger.debug(
            f"Parsed items Json successfully, with {parsedItems} parsed items and {noneCounter} items that could not be parsed"
        )
        return itemsList

    #This could be static but for now its ok
    def createMappingStatsDict(self, statsMappingTable:List[StatsMappingTable]) -> Dict[str,str]:
        """
        Create a dict to map stats names from riot api to "better names"(IMO) using a table in the database 
        called StatsMappingTable, it just has two rows one with the riot stat name and another with the custom name 
        """
        mapping : Dict[str,str] = {}
        for row in statsMappingTable:
            mapping[row.original_name] = row.mapped_name
        return mapping

    async def parseDataNodeIntoItem(
        self, itemId: int, itemData, itemNames: Set[str], statMapping:Dict[str,str]
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
                    f"'name' node has the value {itemData["name"]} register multiple times, just one  (the first) will be register in the database"
                )
                return None
            return Item(
                name=itemData["name"],
                id=itemId,
                plaintext=itemData["plaintext"],
                image=itemData["image"]["full"],
                imageUrl=self.buildImageUrl(itemData["image"]["full"]),
                gold=Gold(**itemData["gold"]) if "gold" in itemData else Gold(base=0, purchasable=False, total=0, sell=0),
                tags=set(itemData["tags"]) if "tags" in itemData else set(),
                stats=self.parseStatsNodeIntoStats(itemData["stats"], statMapping) if "stats" in itemData else set(),
                description=itemData["description"],
                effect=Effects(root=itemData["effect"]) if "effect" in itemData else Effects(root={}),
            )
        except Exception as e:
            logger.exception(
                f"Error, the item with id {itemId} and item data {itemData} had a problem while parsing the json into an Item, this item will be ingnore, exception : {e}"
            )
            return None

    def parseStatsNodeIntoStats(self, statsNode:Dict[str,int | float], statMappingDict : Dict[str,str]) -> Set[Stat]:
        """
        Parse the stat node into a stat list 
        Raises nothing
        """
        stats:Set[Stat] = set()
        for statOriginalName, statValue in statsNode.items():
            statKind : str = "flat"
            if "Flat" not in statOriginalName or "Percent" not in statOriginalName:
                logger.warning(f"Stat mapping error, stat with original name {statOriginalName} has no flat or percent in the name, cant decide the kind of stat, default is flat")
            if "Percent" in statOriginalName:
                statKind = "percentage"
            statMappedName : str = statOriginalName
            if statOriginalName in statMappingDict:
                statMappedName = statMappingDict[statOriginalName]
            stat:Stat= Stat(name = statMappedName, value = statValue, kind=statKind)
            stats.add(stat)
        return stats
    

    def buildImageUrl(self, imageName : str) -> str:
        """
        Build the image url given the version and image name
        """
        return f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/item/{imageName}"

    async def updateTagsInDataBase(self, tagsToAdd: Set[str]) -> None:
        """
        Given a set of unique tags, iterate over them and update the tags table
        Raise UpdateTagsError
        """
        logger.debug("Updating tags table")
        try:
            logger.debug("Getting existing tags in the database")
            existingTagNames: Set[str] = await getAllTagsTableNames(self.dbSession)
            logger.debug(f"Got {len(existingTagNames)} from database")
        except Exception as e:
            logger.error(
                f"Error, could not get existing tag names in the database: {e}"
            )
            raise UpdateTagsError() from e
        logger.debug(f"Adding {len(tagsToAdd)} tags, just new tags will be added")
        newAditions: int = 0
        for tag in tagsToAdd:
            isNew: bool = self.addTagInDataBaseIfNew(tag, existingTagNames)
            if isNew:
                newAditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            logger.error(f"An error occurred while commiting tags update: {e}")
            await self.dbSession.rollback()
            raise UpdateTagsError() from e
        logger.debug(f"Updated tags table successfully, {newAditions} new tags added")

    def addTagInDataBaseIfNew(self, tag: str, existingTagNames: Set[str]) -> bool:
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

    async def updateStatsInDataBase(self, statsToAdd: Set[Stat]) -> None:
        """
        Given a set of unique stats, iterate over them and update the stats table
        Raise UpdateStatsError
        """
        logger.debug("Updating stats table")
        try:
            logger.debug("Getting existing stats in the database")
            existingStatNames: Set[str] = await getAllStatsTableNames(self.dbSession)
            logger.debug(f"Got {len(existingStatNames)} from database")
        except SQLAlchemyError as e:
            logger.error(
                f"Error, could not get existing stat names in the database: {e}"
            )
            raise UpdateStatsError() from e
        logger.debug(f"Adding {len(statsToAdd)} stats, just new stats will be added")
        newAditions: int = 0
        for stat in statsToAdd:
            isNew: bool = self.addStatInDataBaseIfNew(stat, existingStatNames)
            if isNew:
                newAditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            logger.error(f"An error occurred while commiting stats update: {e}")
            await self.dbSession.rollback()
            raise UpdateStatsError() from e
        logger.debug(f"Updated stats table successfully, {newAditions} new stats added")

    async def updateEffectsInDataBase(self, effectsToAdd: Set[str]) -> None:
        """
        Given a set of unique effects, iterate over them and update the effects table.
        Raises UpdateEffectsError.
        """
        logger.debug("Updating effects table")
        try:
            logger.debug("Getting existing effects from the database")
            existingEffectNames: Set[str] = await getAllEffectsTableNames(
                self.dbSession
            )
            logger.debug(f"Got {len(existingEffectNames)} from database")
        except SQLAlchemyError as e:
            logger.error(
                f"Error, could not get existing effect names in the database: {e}"
            )
            raise UpdateEffectsError() from e

        logger.debug(
            f"Adding {len(effectsToAdd)} effects, only new effects will be added"
        )
        newAdditions: int = 0
        for effect in effectsToAdd:
            isNew: bool = self.addEffectInDataBaseIfNew(effect, existingEffectNames)
            if isNew:
                newAdditions += 1
        try:
            await self.dbSession.commit()
        except Exception as e:
            logger.error(f"An error occurred while committing effects update: {e}")
            await self.dbSession.rollback()
            raise UpdateEffectsError() from e
        logger.debug(
            f"Updated effects table successfully, {newAdditions} new effects added"
        )

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
            logger.error(f"Error while updating effect {effect}, exception: {e}")
            raise UpdateEffectsError() from e

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
            logger.error(f"Error while updating stat {stat.name}, kind {stat.kind}, exception: {e}")
            raise UpdateStatsError() from e

    async def updateItemsInDataBase(self, itemsList: List[Item]) -> None:
        """
        Updates the items in the database, transactions are added in a batch,
        if the insert/update fails then the transacion fails and changes are rollback.
        """
        logger.debug(f"Updating {len(itemsList)} items in the database")
        currentItemName: str = ""
        try:
            for item in itemsList:
                currentItemName = item.name
                existingItem: ItemTable | None = await getItemTableGivenItemName(
                    self.dbSession, item.name
                )
                await self.insertOrUpdateItemTable(item, existingItem)
            await self.dbSession.commit()
            logger.debug(f"Updated {len(itemsList)} items successfully")
        except SQLAlchemyError as e:
            logger.debug(
                f"Error getting the item from the database with name {currentItemName}, exception: {e}"
            )
            await self.dbSession.rollback()
            raise UpdateItemsError() from e
        except Exception as e:
            logger.debug(
                f"Error inserting/updating an item in the database with name {currentItemName}, exception: {e}"
            )
            await self.dbSession.rollback()
            raise UpdateItemsError() from e

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
            #Here the linter gives an error because stats, effects or tags can be None but in reality 
            #the default constructor is empty so I think its fine
            await self.addItemStatsRelations(itemTable.id, item.stats)
            await self.addItemEffectsRelations(itemTable.id, item.effect)
            await self.addItemTagsRelations(itemTable.id, item.tags)
        except UpdateItemsError as e:
            raise e
        except Exception as e:
            logger.error(
                f"Unexpected exception happened insering/updating the item {item.name}, exception : {e}"
            )
            raise UpdateItemsError() from e

    async def addItemStatsRelations(self, itemId: int, stats: Set[Stat]) -> None:
        """
        This function inserts the relations given the itemId and stats
        Raises UpdateItemsError when something fails
        """
        for stat in stats:
            statId: int | None = await getStatIdWithStatName(self.dbSession, stat.name)
            if statId is None:
                logger.error(f"Stat with name {stat} was not found in the dabatase")
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
                    logger.error(
                        f"Could not insert a relation item-stat, itemId: {itemId}, statId: {statId}, statName: {stat}, exception: {e}"
                    )
                    raise UpdateItemsError(
                        "Could not insert a relation item-stat"
                    ) from e

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
                logger.error(f"Effect with name {effect} was not found in the database")
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
                    logger.error(
                        f"Could not insert a relation item-effect, itemId: {itemId}, effectId: {effectId}, effectName: {effect}, exception: {e}"
                    )
                    raise UpdateItemsError(
                        "Could not insert a relation item-effect"
                    ) from e

    async def addItemTagsRelations(self, itemId: int, tags: Set[str]) -> None:
        """
        This function inserts the relations given the itemId and tags
        Raises UpdateItemsError when something fails
        """
        for tag in tags:
            tagId: int | None = await getTagIdWithtTagName(self.dbSession, tag)
            if tagId is None:
                logger.error(f"Tag with name {tag} was not found in the dabatase")
                raise UpdateItemsError("Tag was not found in the database")
            itemtagsValues: dict = {"item_id": itemId, "tags_id": tagId}
            try:
                ins = insert(ItemTagsAssociation).values(**itemtagsValues)
                await self.dbSession.execute(ins)
            except Exception as e:
                logger.error(
                    f"Could not insert a relation item-tag, itemId: {itemId}, tagId: {tagId}, tagName: {tag}, exception: {e}"
                )
                raise UpdateItemsError("Could not insert a relation item-tag") from e

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
            logger.error(
                f"Error while deleting tags associations for item id {itemId}: {e}"
            )
            raise UpdateItemsError("Error while deleting tags associations for item")

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
            logger.error(
                f"Error while deleting stats associations for item id {itemId}: {e}"
            )
            raise UpdateItemsError("Error while deleting stats associations for item")

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
            logger.error(
                f"Error while deleting effects associations for item id {itemId}: {e}"
            )
            raise UpdateItemsError("Error while deleting effects associations for item")

    async def insertOrUpdateGoldTable(
        self, createNewGoldTable: bool, gold: Gold, itemId: int | None = None
    ) -> int:
        """
        Insert or updates the gold table depending on the createNewGoldTable parameter
        Raises UpdateItemsError
        """
        if (itemId is None) and (createNewGoldTable is False):
            logger.error(
                "Error trying to updating a gold table the item id can not be None"
            )
            raise UpdateItemsError("Can not update a gold table with no item id")
        newGoldTable: GoldTable = mapGoldToGoldTable(gold)
        if (createNewGoldTable is False) and (itemId is not None):
            existingGoldTableId: int | None = await getGoldIdWithItemId(
                self.dbSession, itemId
            )
            if existingGoldTableId is None:
                logger.error(
                    f"Error updating the row in gold table with item id {itemId}, did not find the row with goldId {existingGoldTableId}"
                )
                raise UpdateItemsError("Tried to update a gold row that do not exist")
            newGoldTable.id = existingGoldTableId
        try:
            newGoldTable = await self.dbSession.merge(newGoldTable)
            await self.dbSession.flush()
            return newGoldTable.id
        except Exception as e:
            logger.error(f"Error updating/inserting a gold table, exception: {e}")
            raise UpdateItemsError(
                "Unexpected exception happened while inserting/updating a gold row"
            ) from e

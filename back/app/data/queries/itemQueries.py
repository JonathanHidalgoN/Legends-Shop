from typing import Dict, List, Set, Tuple
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.MetaDataTable import MetaDataTable
from app.data.models.EffectsTable import EffectsTable, ItemEffectAssociation
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.StatsMappingTable import StatsMappingTable
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import (
    ItemTagsAssociation,
    TagsTable,
)
from app.logger import logger
from app.schemas.Item import Stat


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    """Fetch all tags from the TagsTable."""
    result = await asyncSession.execute(select(TagsTable))
    existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags


async def getItemTableByItemId(
    asyncSession: AsyncSession, itemId: int
) -> ItemTable | None:
    """Retrun itemTable with the item ID"""
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.id == itemId))
    itemTable: ItemTable = result.scalars().first()
    if itemTable:
        return itemTable
    else:
        logger.warning(f"Tried to get itemTable with id {itemId} but None was found")
        return None


async def getAllTagNamesAssociatedByItemId(
    asyncSession: AsyncSession, itemId: int
) -> Set[str]:
    """Return all tag names linked to the specified item ID."""
    result = await asyncSession.execute(
        select(ItemTagsAssociation.c.tags_id).where(
            ItemTagsAssociation.c.item_id == itemId
        )
    )
    # Here can use scalars because just getting tags_id from select
    tagsId: Set[int] = set(tagId for tagId in result.scalars().all())
    tagNames: Set[str] = set()
    for tagId in tagsId:
        tagName: str | None = await getTagNameWithId(asyncSession, tagId)
        if tagName:
            tagNames.add(tagName)
    return tagNames


async def getTagNameWithId(asyncSession: AsyncSession, tagId: int) -> str | None:
    """Retrieve a tag's name using its ID."""
    result = await asyncSession.execute(
        select(TagsTable.name).where(TagsTable.id == tagId)
    )
    tagName = result.scalars().first()
    if tagName:
        return tagName
    else:
        logger.warning(f"Tried to get tagName with id {tagId} but None was found")
        return None


async def getStatSetByItemId(
    asyncSession: AsyncSession, itemId: int
) -> Set[Stat]:
    """Return a set of stats pairs for the given item ID."""
    result = await asyncSession.execute(
        select(ItemStatAssociation.c.stat_id, ItemStatAssociation.c.value).where(
            ItemStatAssociation.c.item_id == itemId
        )
    )
    # Here can´t use scalars because it is a Table, not an ORM model
    statsIdValue: Set[Row[Tuple[int, int | float]]] = set(result.all())
    stats: Set[Stat] = set() 
    for statTuple in statsIdValue:
        statTable: StatsTable | None = await getStatTableWithId(asyncSession, statTuple[0])
        if statTable:
            #Linter error but kind must be percentage or flat so ignore it
            stat: Stat = Stat(name=statTable.name, kind=statTable.kind, value = statTuple[1])  
            stats.add(stat)
    return stats 


async def getStatTableWithId(asyncSession: AsyncSession, statId: int) -> StatsTable | None:
    """Retrieve the stat table of a stat given its ID."""
    result = await asyncSession.execute(
        select(StatsTable).where(StatsTable.id == statId)
    )
    stat = result.scalars().first()
    if stat:
        return stat
    else:
        logger.warning(f"Tried to get statName with id {statId} but None was found")
        return None


async def getAllEffectNamesAndValueAssociatedByItemId(
    asyncSession: AsyncSession, itemId: int
) -> Dict[str, int | float]:
    """Return a set of effect name/value pairs for the given item ID."""
    result = await asyncSession.execute(
        select(ItemEffectAssociation.c.effect_id, ItemEffectAssociation.c.value).where(
            ItemEffectAssociation.c.item_id == itemId
        )
    )
    # Here can´t use scalars because it is a Table, not an ORM model
    effectsIdValue: Set[Row[Tuple[int, int | float]]] = set(result.all())
    effectDicts: Dict[str, int | float] = {}
    for effectTuple in effectsIdValue:
        effectName: str | None = await getEffectNameWithId(asyncSession, effectTuple[0])
        if effectName:
            effectDicts[effectName] = effectTuple[1]
    return effectDicts


async def getEffectNameWithId(asyncSession: AsyncSession, effectId: int) -> str | None:
    """Retrieve the name of a effect given its ID."""
    result = await asyncSession.execute(
        select(EffectsTable.name).where(EffectsTable.id == effectId)
    )
    effectName = result.scalars().first()
    if effectName:
        return effectName
    else:
        logger.warning(f"Tried to get effectName with id {effectId} but None was found")
        return None


async def getAllTagsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """Return a set of unique tag names from the TagsTable."""
    result = await asyncSession.execute(select(TagsTable.name))
    existingTags: Set[str] = set(tag for tag in result.scalars().all())
    return existingTags


async def getAllStatsTable(asyncSession: AsyncSession) -> List[StatsTable]:
    """Fetch all stat records from the StatsTable."""
    result = await asyncSession.execute(select(StatsTable))
    existingStats: List[StatsTable] = [tag for tag in result.scalars().all()]
    return existingStats


async def getAllStatsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """Return a set of unique stat names from the StatsTable."""
    result = await asyncSession.execute(select(StatsTable.name))
    existingStats: Set[str] = set(tag for tag in result.scalars().all())
    return existingStats


async def getAllEffectsTable(asyncSession: AsyncSession) -> List[EffectsTable]:
    """Fetch all effect records from the EffectsTable."""
    result = await asyncSession.execute(select(EffectsTable))
    existingEffects: List[EffectsTable] = [tag for tag in result.scalars().all()]
    return existingEffects


async def getAllEffectsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """Return a set of unique effect names from the EffectsTable."""
    result = await asyncSession.execute(select(EffectsTable.name))
    existingEffects: Set[str] = set(tag for tag in result.scalars().all())
    return existingEffects


async def getItemTableGivenItemName(
    asyncSession: AsyncSession, name: str
) -> ItemTable | None:
    """Retrieve an item from the ItemTable by its name."""
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.name == name))
    itemTable = result.scalars().first()
    if itemTable:
        return itemTable
    else:
        logger.warning(
            f"Tried to get itemTable with item name {name} but None was found"
        )
        return None


async def getItems(asyncSession: AsyncSession) -> List[ItemTable]:
    """Fetch all items from the ItemTable."""
    result = await asyncSession.execute(select(ItemTable))
    items: List[ItemTable] = [item for item in result.scalars().all()]
    return items

async def getSomeItems(asyncSession: AsyncSession) -> List[ItemTable]:
    """Fetch some items from the ItemTable."""
    result = await asyncSession.execute(select(ItemTable).limit(100))
    items: List[ItemTable] = [item for item in result.scalars().all()]
    return items


async def getStatIdWithStatName(
    asyncSession: AsyncSession, statName: str
) -> int | None:
    """Get the ID of a stat based on its name."""
    result = await asyncSession.execute(
        select(StatsTable.id).where(StatsTable.name == statName)
    )
    stat = result.scalars().first()
    if stat:
        return stat
    else:
        logger.warning(
            f"Tried to get stat id item  stat name {statName} but None was found"
        )
        return None


async def getEffectIdWithEffectName(
    asyncSession: AsyncSession, effectName: str
) -> int | None:
    """Retrieve the ID of an effect by its name."""
    result = await asyncSession.execute(
        select(EffectsTable.id).where(EffectsTable.name == effectName)
    )
    effect = result.scalars().first()
    return effect if effect else None


async def getGoldIdWithItemId(asyncSession: AsyncSession, itemId: int) -> int | None:
    """Fetch the gold ID associated with a given item ID."""
    result = await asyncSession.execute(
        select(ItemTable.gold_id).where(ItemTable.id == itemId)
    )
    goldId = result.scalars().first()
    if goldId:
        return goldId
    else:
        logger.warning(f"Tried to get gold if with item id {itemId} but None was found")
        return None


async def getGoldTableWithId(
    asyncSession: AsyncSession, goldId: int
) -> GoldTable | None:
    """Retrieve gold details by gold ID."""
    result = await asyncSession.execute(select(GoldTable).where(GoldTable.id == goldId))
    goldTable = result.scalars().first()
    if goldTable:
        return goldTable
    else:
        logger.warning(f"Tried to get gold table with id {goldId} but None was found")
        return None


async def getGoldTableWithItemId(
    asyncSession: AsyncSession, itemId: int
) -> GoldTable | None:
    """Get gold information for a given item by its item ID."""
    goldId: int | None = await getGoldIdWithItemId(asyncSession, itemId)
    if goldId is None:
        return None
    result = await asyncSession.execute(select(GoldTable).where(GoldTable.id == goldId))
    goldTable = result.scalars().first()
    goldTable = result.scalars().first()
    if goldTable:
        return goldTable
    else:
        logger.warning(
            f"Tried to get gold table with item id {itemId} but None was found"
        )
        return None


async def getTagIdWithtTagName(asyncSession: AsyncSession, tagName: str) -> int | None:
    """Fetch the ID of a tag using its name."""
    result = await asyncSession.execute(
        select(TagsTable.id).where(TagsTable.name == tagName)
    )
    tag = result.scalars().first()
    if tag:
        return tag
    else:
        logger.warning(f"Trid to get tag id with tag name {tagName} but None was found")
        return None


async def getVersion(asyncSession: AsyncSession) -> str | None:
    """Retrieve the application version from the metadata."""
    result = await asyncSession.execute(
        select(MetaDataTable.value).where(MetaDataTable.field_name == "version")
    )
    version = result.scalars().first()
    if version:
        return version
    else:
        logger.warning(f"Tried to get version but None was found")
    return version if version else None


async def updateVersion(asyncSession: AsyncSession, version: str) -> None:
    """Update the application version in the metadata table."""
    async with asyncSession.begin():
        versionRow: MetaDataTable = MetaDataTable(field_name="version", value=version)
        await asyncSession.merge(versionRow)

async def getStatsMappingTable(asyncSession: AsyncSession) -> List[StatsMappingTable]:
    """Get the stats mapping table"""
    result = await asyncSession.execute(
        select(StatsMappingTable)
    )
    statsMappingTable : List[StatsMappingTable] = [row for row in result.scalars().all()] 
    return statsMappingTable 


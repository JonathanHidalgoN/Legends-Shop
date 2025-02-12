from typing import Dict, List, Set, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.MetaDataTable import MetaDataTable
from app.data.models.EffectsTable import EffectsTable, ItemEffectAssociation
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.ImageTable import ImageTable 
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import (
    ItemTagsAssociation,
    TagsTable,
)


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    """Fetch all tags from the TagsTable."""
    result = await asyncSession.execute(select(TagsTable))
    existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags

# async def getImageByItemId(asyncSession, itemId:int)->ImageTable | None:
#     result = 
#     result = await asyncSession.execute(select(ImageTable.id))
#

async def getItemTableByItemId(asyncSession : AsyncSession, itemId : int) -> ItemTable | None:
    """Retrun itemTable with the item ID"""
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.id == itemId))
    itemTable : ItemTable = result.scalars().first()
    return itemTable if itemTable else None


async def getAllTagNamesAssociatedByItemId(asyncSession: AsyncSession, itemId: int) -> Set[str]:
    """Return all tag names linked to the specified item ID."""
    result = await asyncSession.execute(
        select(ItemTagsAssociation.c.tags_id)
        .where(ItemTagsAssociation.c.item_id == itemId)
    )
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
    return tagName if tagName else None


async def getAllStatNamesAndValueAssociatedByItemId(asyncSession: AsyncSession, itemId: int) -> Dict[str, int | float]:
    """Return a set of stat name/value pairs for the given item ID."""
    result = await asyncSession.execute(
        select(ItemStatAssociation)
        .where(ItemStatAssociation.c.item_id == itemId)
    )
    statsIdValue: Set[Tuple[int, int]] = set(
        (statAssociationRow.c.item_id, statAssociationRow.c.value)
        for statAssociationRow in result.scalars().all()
    )
    statDicts: Dict[str, int | float] = {}
    for statTuple in statsIdValue:
        statName: str | None = await getStatNameWithId(asyncSession, statTuple[0])
        if statName:
            statDicts[statName] = statTuple[1]
    return statDicts


async def getStatNameWithId(asyncSession: AsyncSession, statId: int) -> str | None:
    """Retrieve the name of a stat given its ID."""
    result = await asyncSession.execute(
        select(StatsTable.name).where(StatsTable.id == statId)
    )
    statName = result.scalars().first()
    return statName if statName else None


async def getAllEffectNamesAndValueAssociatedByItemId(asyncSession: AsyncSession, itemId: int) -> Dict[str, int | float]:
    """Return a set of effect name/value pairs for the given item ID."""
    result = await asyncSession.execute(
        select(ItemEffectAssociation)
        .where(ItemEffectAssociation.c.item_id == itemId)
    )
    effectsIdValue: Set[Tuple[int, int]] = set(
        (effectAssociationRow.c.item_id, effectAssociationRow.c.value)
        for effectAssociationRow in result.scalars().all()
    )
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
    return effectName if effectName else None


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


async def getItemTableGivenItemName(asyncSession: AsyncSession, name: str) -> ItemTable | None:
    """Retrieve an item from the ItemTable by its name."""
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.name == name))
    itemTable = result.scalars().first()
    return itemTable if itemTable else None


async def getItems(asyncSession: AsyncSession) -> List[ItemTable]:
    """Fetch all items from the ItemTable."""
    result = await asyncSession.execute(select(ItemTable))
    items: List[ItemTable] = [item for item in result.scalars().all()]
    return items


async def getStatIdWithStatName(asyncSession: AsyncSession, statName: str) -> int | None:
    """Get the ID of a stat based on its name."""
    result = await asyncSession.execute(
        select(StatsTable.id).where(StatsTable.name == statName)
    )
    stat = result.scalars().first()
    return stat if stat else None


async def getEffectIdWithEffectName(asyncSession: AsyncSession, effectName: str) -> int | None:
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
    return goldId if goldId else None


async def getGoldTableWithId(asyncSession: AsyncSession, goldId: int) -> GoldTable | None:
    """Retrieve gold details by gold ID."""
    result = await asyncSession.execute(
        select(GoldTable).where(GoldTable.id == goldId)
    )
    goldTable = result.scalars().first()
    return goldTable if goldTable else None


async def getGoldTableWithItemId(asyncSession: AsyncSession, itemId: int) -> GoldTable | None:
    """Get gold information for a given item by its item ID."""
    goldId: int | None = await getGoldIdWithItemId(asyncSession, itemId)
    if goldId is None:
        return None
    result = await asyncSession.execute(select(GoldTable).where(GoldTable.id == goldId))
    goldTable = result.scalars().first()
    return goldTable if goldTable else None


async def getTagIdWithtTagName(asyncSession: AsyncSession, tagName: str) -> int | None:
    """Fetch the ID of a tag using its name."""
    result = await asyncSession.execute(
        select(TagsTable.id).where(TagsTable.name == tagName)
    )
    tag = result.scalars().first()
    return tag if tag else None


async def getVersion(asyncSession: AsyncSession) -> str | None:
    """Retrieve the application version from the metadata."""
    result = await asyncSession.execute(
        select(MetaDataTable.value).where(MetaDataTable.name == "version")
    )
    version = result.scalars().first()
    return version if version else None


async def updateVersion(asyncSession: AsyncSession, version: str) -> None:
    """Update the application version in the metadata table."""
    async with asyncSession.begin():
        versionRow: MetaDataTable = MetaDataTable(field_name="version", value=version)
        await asyncSession.merge(versionRow)

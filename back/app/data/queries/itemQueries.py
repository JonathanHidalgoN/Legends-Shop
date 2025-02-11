from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.MetaDataTable import MetaDataTable
from app.data.models.EffectsTable import EffectsTable
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.StatsTable import StatsTable
from app.data.models.TagsTable import (
    TagsTable,
)


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    result = await asyncSession.execute(select(TagsTable))
    existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags


async def getAllTagsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """
    Returns a set(because tag names are unique) with tag names
    """
    result = await asyncSession.execute(select(TagsTable.name))
    existingTags: Set[str] = set(tag for tag in result.scalars().all())
    return existingTags


async def getAllStatsTable(asyncSession: AsyncSession) -> List[StatsTable]:
    result = await asyncSession.execute(select(StatsTable))
    existingStats: List[StatsTable] = [tag for tag in result.scalars().all()]
    return existingStats


async def getAllStatsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """
    Returns a set(because stats names are unique) with stat names
    """
    result = await asyncSession.execute(select(StatsTable.name))
    existingStats: Set[str] = set(tag for tag in result.scalars().all())
    return existingStats


async def getAllEffectsTable(asyncSession: AsyncSession) -> List[EffectsTable]:
    result = await asyncSession.execute(select(EffectsTable))
    existingEffects: List[EffectsTable] = [tag for tag in result.scalars().all()]
    return existingEffects


async def getAllEffectsTableNames(asyncSession: AsyncSession) -> Set[str]:
    """
    Returns a set (because effect names are unique) with effect names.
    """
    result = await asyncSession.execute(select(EffectsTable.name))
    existingEffects: Set[str] = set(tag for tag in result.scalars().all())
    return existingEffects


async def getItemTableGivenItemName(
    asyncSession: AsyncSession, name: str
) -> ItemTable | None:
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.name == name))
    itemTable = result.scalars().first()
    return itemTable if itemTable else None


async def getItems(asyncSession: AsyncSession) -> List[ItemTable]:
    result = await asyncSession.execute(select(ItemTable))
    items : List[ItemTable] = [item for  item in result.scalars().all()]
    return items 

async def getStatIdWithStatName(
    asyncSession: AsyncSession, statName: str
) -> int | None:
    result = await asyncSession.execute(
        select(StatsTable.id).where(StatsTable.name == statName)
    )
    stat = result.scalars().first()
    return stat if stat else None


async def getEffectIdWithEffectName(
    asyncSession: AsyncSession, effectName: str
) -> int | None:
    result = await asyncSession.execute(
        select(EffectsTable.id).where(EffectsTable.name == effectName)
    )
    effect = result.scalars().first()
    return effect if effect else None


async def getGoldIdWithItemId(asyncSession: AsyncSession, itemId: int) -> int | None:
    result = await asyncSession.execute(
        select(ItemTable.gold_id).where(ItemTable.id == itemId)
    )
    goldId = result.scalars().first()
    return goldId if goldId else None

async def getGoldTableWithId(asyncSession: AsyncSession, goldId: int) -> GoldTable | None:
    result = await asyncSession.execute(
        select(GoldTable).where(GoldTable.id == goldId)
    )
    goldTable = result.scalars().first()
    return goldTable if goldTable else None

async def getGoldTableWithItemId(
    asyncSession: AsyncSession, itemId: int
) -> GoldTable | None:
    goldId: int | None = await getGoldIdWithItemId(asyncSession, itemId)
    if goldId is None:
        return None
    result = await asyncSession.execute(select(GoldTable).where(GoldTable.id == goldId))
    goldTable = result.scalars().first()
    return goldTable if goldTable else None


async def getTagIdWithtTagName(asyncSession: AsyncSession, tagName: str) -> int | None:
    result = await asyncSession.execute(
        select(TagsTable.id).where(TagsTable.name == tagName)
    )
    tag = result.scalars().first()
    return tag if tag else None


async def getVersion(asyncSession: AsyncSession) -> str | None:
    result = await asyncSession.execute(
        select(MetaDataTable.value).where(MetaDataTable.name == "version")
    )
    version = result.scalars().first()
    return version if version else None


async def updateVersion(asyncSession: AsyncSession, version: str) -> None:
    async with asyncSession.begin():
        versionRow: MetaDataTable = MetaDataTable(field_name="version", value=version)
        await asyncSession.merge(versionRow)

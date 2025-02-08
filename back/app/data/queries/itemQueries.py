from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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


async def getItemTableGivenItemName(
    asyncSession: AsyncSession, name: str
) -> ItemTable | None:
    result = await asyncSession.execute(select(ItemTable).where(ItemTable.name == name))
    itemTable = result.scalars().first()
    return itemTable if itemTable else None


async def getStatIdWithStatName(
    asyncSession: AsyncSession, statName: str
) -> int | None:
    result = await asyncSession.execute(
        select(StatsTable.id).where(StatsTable.name == statName)
    )
    stat = result.scalars().first()
    return stat if stat else None


async def getGoldIdWithItemId(asyncSession: AsyncSession, itemId: int) -> int | None:
    result = await asyncSession.execute(
        select(ItemTable.gold_id).where(ItemTable.id == itemId)
    )
    goldId = result.scalars().first()
    return goldId if goldId else None


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

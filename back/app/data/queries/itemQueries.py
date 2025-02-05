from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import (
    TagsTable,
)
from app.schemas.Item import Gold


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    result = await asyncSession.execute(select(TagsTable))
    existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags


async def getAllTagsTableNames(asyncSession: AsyncSession) -> List[str]:
    result = await asyncSession.execute(select(TagsTable.name))
    existingTags: List[str] = [tag for tag in result.scalars().all()]
    return existingTags


async def getAllStatsTable(asyncSession: AsyncSession) -> List[StatsTable]:
    result = await asyncSession.execute(select(StatsTable))
    existingStats: List[StatsTable] = [tag for tag in result.scalars().all()]
    return existingStats


async def getAllStatsTableNames(asyncSession: AsyncSession) -> List[str]:
    result = await asyncSession.execute(select(StatsTable.name))
    existingStats: List[str] = [tag for tag in result.scalars().all()]
    return existingStats

async def getItemTableGivenName(asyncSession: AsyncSession, name : str) -> ItemTable | None:
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


# async def getGoldIdWithItemId(asyncSession: AsyncSession, itemId:int) -> int | None:
#     result = await asyncSession.execute(select(ItemTable.gold_id).where(ItemTable.id == itemId))
#     goldId = result.scalars().first()
#     return goldId if goldId else None

    # if not goldId:
    #     return None
    # result = await asyncSession.execute(select(GoldTable).where(GoldTable.id == goldId))

# async def getGoldTableWithItemId(asyncSession: AsyncSession, itemId:int) -> GoldTable | None:



async def getTagIdWithtTagName(asyncSession: AsyncSession, tagName: str) -> int | None:
    result = await asyncSession.execute(
        select(TagsTable.id).where(TagsTable.name == tagName)
    )
    tag = result.scalars().first()
    return tag if tag else None

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.TagsTable import (
    TagsTable,
)


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    async with asyncSession.begin():
        result = await asyncSession.execute(select(TagsTable))
        existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags


async def getAllTagsTableNames(asyncSession: AsyncSession) -> List[str]:
    async with asyncSession.begin():
        result = await asyncSession.execute(select(TagsTable))
        existingTags: List[str] = [tag.name for tag in result.scalars().all()]
    return existingTags


async def getAllStatsTable(asyncSession: AsyncSession) -> List[StatsTable]:
    async with asyncSession.begin():
        result = await asyncSession.execute(select(StatsTable))
        existingStats: List[StatsTable] = [tag for tag in result.scalars().all()]
    return existingStats


async def getAllStatsTableNames(asyncSession: AsyncSession) -> List[str]:
    async with asyncSession.begin():
        result = await asyncSession.execute(select(StatsTable))
        existingStats: List[str] = [tag.name for tag in result.scalars().all()]
    return existingStats


async def getStatIdWithStatName(
    asyncSession: AsyncSession, statName: str
) -> int | None:
    async with asyncSession.begin():
        result = await asyncSession.execute(
            select(StatsTable).where(StatsTable.name == statName)
        )
        stat = result.scalars().first()
    return stat.id if stat else None

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.data.models.TagsTable import (
    TagsTable,
)


async def getAllTagsTable(asyncSession: AsyncSession) -> List[TagsTable]:
    async with asyncSession.begin():
        result = await asyncSession.execute(select(TagsTable))
        existingTags: List[TagsTable] = [tag for tag in result.scalars().all()]
    return existingTags


async def getAllTagsTableNames(asyncSession: AsyncSession) -> List[str]:
    # Using select to query the TagsTable
    async with asyncSession.begin():
        result = await asyncSession.execute(select(TagsTable))
        existingTags: List[str] = [tag.name for tag in result.scalars().all()]
    return existingTags

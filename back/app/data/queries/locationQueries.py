from typing import List, Sequence, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.models.LocationTable import LocationTable


async def getAllLocationIds(asyncSession: AsyncSession) -> Sequence[int]:
    """Return a list of location IDs."""
    result = await asyncSession.execute(select(LocationTable.id))
    locations: Sequence[int] = result.scalars().all()
    return locations


async def getLocationIdByCountryName(asyncSession: AsyncSession, countryName: str) -> int | None:
    """Return location ID for a given country name."""
    result = await asyncSession.execute(
        select(LocationTable.id).where(LocationTable.country_name == countryName)
    )
    locationId: int | None = result.scalars().first()
    return locationId


async def getCountryNameById(asyncSession: AsyncSession, locationId: int) -> str | None:
    """Return country name for a given location ID."""
    result = await asyncSession.execute(
        select(LocationTable.country_name).where(LocationTable.id == locationId)
    )
    countryName: str | None = result.scalars().first()
    return countryName 

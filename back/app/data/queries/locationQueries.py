from typing import List, Sequence, Tuple, Optional
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


async def getAllLocations(asyncSession: AsyncSession) -> List[LocationTable]:
    """Get all locations from the database."""
    result = await asyncSession.execute(select(LocationTable))
    return list(result.scalars().all())


async def getLocationById(asyncSession: AsyncSession, locationId: int) -> Optional[LocationTable]:
    """Get a location by its ID."""
    result = await asyncSession.execute(
        select(LocationTable).where(LocationTable.id == locationId)
    )
    return result.scalar_one_or_none()


async def getLocationByCountryName(asyncSession: AsyncSession, countryName: str) -> Optional[LocationTable]:
    """Get a location by its country name."""
    result = await asyncSession.execute(
        select(LocationTable).where(LocationTable.country_name == countryName)
    )
    return result.scalar_one_or_none()


async def createLocation(asyncSession: AsyncSession, countryName: str) -> None:
    """Create a new location."""
    location = LocationTable(country_name=countryName)
    asyncSession.add(location)
    await asyncSession.flush()


async def updateLocation(asyncSession: AsyncSession, locationId: int, newCountryName: str) -> None:
    """Update a location's country name."""
    location = await getLocationById(asyncSession, locationId)
    if location:
        location.country_name = newCountryName
        await asyncSession.flush()


async def deleteLocation(asyncSession: AsyncSession, locationId: int) -> None:
    """Delete a location by its ID."""
    location = await getLocationById(asyncSession, locationId)
    if location:
        await asyncSession.delete(location)
        await asyncSession.flush() 
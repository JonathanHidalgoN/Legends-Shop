from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.data.models.LocationTable import LocationTable
from app.data.queries.locationQueries import (
    createLocation,
    deleteLocation,
    getLocationById,
    getLocationByCountryName,
    updateLocation,
    getAllLocations,
)
from app.customExceptions import (
    LocationAlreadyExistsException,
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.auth.functions import logMethod
from typing import List
from app.schemas.Location import Location
from app.data.mappers import mapLocationTableToLocation


class LocationManager:
    def __init__(self, asyncSession: AsyncSession):
        self.dbSession = asyncSession

    @logMethod
    async def createLocation(self, countryName: str) -> None:
        """
        Create a new location with the given country name.

        Args:
            countryName (str): The name of the country for the new location.

        Raises:
            LocationAlreadyExistsException: If a location with the same country name already exists.
            LocationManagerException: If there's an error creating the location.
        """
        try:
            existingLocation = await getLocationByCountryName(
                self.dbSession, countryName
            )
            if existingLocation:
                raise LocationAlreadyExistsException(
                    f"Location with country name '{countryName}' already exists"
                )

            await createLocation(self.dbSession, countryName)
            await self.dbSession.commit()
        except IntegrityError as e:
            await self.dbSession.rollback()
            raise LocationAlreadyExistsException(
                f"Location with country name '{countryName}' already exists"
            ) from e
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationManagerException(f"Error creating location: {str(e)}") from e

    @logMethod
    async def updateLocation(self, locationId: int, newCountryName: str) -> None:
        """
        Update a location's country name.

        Args:
            locationId (int): The ID of the location to update.
            newCountryName (str): The new country name for the location.

        Raises:
            LocationNotFoundException: If the location is not found.
            LocationUpdateError: If there's an error updating the location.
        """
        try:
            location = await getLocationById(self.dbSession, locationId)
            if not location:
                raise LocationNotFoundException(
                    f"Location with ID {locationId} not found"
                )

            await updateLocation(self.dbSession, locationId, newCountryName)
            await self.dbSession.commit()
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationUpdateError(f"Error updating location: {str(e)}") from e

    @logMethod
    async def deleteLocation(self, locationId: int) -> None:
        """
        Delete a location by its ID.

        Args:
            locationId (int): The ID of the location to delete.

        Raises:
            LocationNotFoundException: If the location is not found.
            LocationDeleteError: If there's an error deleting the location.
        """
        try:
            location = await getLocationById(self.dbSession, locationId)
            if not location:
                raise LocationNotFoundException(
                    f"Location with ID {locationId} not found"
                )

            await deleteLocation(self.dbSession, locationId)
            await self.dbSession.commit()
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationDeleteError(f"Error deleting location: {str(e)}") from e

    @logMethod
    async def getLocation(self, locationId: int) -> Location:
        """
        Get a location by its ID.

        Args:
            locationId (int): The ID of the location to retrieve.

        Returns:
            Location: The requested location.

        Raises:
            LocationNotFoundException: If the location is not found.
        """
        location = await getLocationById(self.dbSession, locationId)
        if not location:
            raise LocationNotFoundException(f"Location with ID {locationId} not found")
        return mapLocationTableToLocation(location)

    @logMethod
    async def getAllLocations(self) -> List[Location]:
        """
        Retrieves all locations from the database.

        Returns:
            List[Location]: List of all locations.

        Raises:
            LocationManagerException: If there's an error retrieving the locations.
        """
        try:
            locations = await getAllLocations(self.dbSession)
            return [mapLocationTableToLocation(location) for location in locations]
        except SQLAlchemyError as e:
            raise LocationManagerException(
                f"Error retrieving locations: {str(e)}"
            ) from e

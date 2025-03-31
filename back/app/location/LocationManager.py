from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.data.models.LocationTable import LocationTable
from app.data.queries.locationQueries import (
    createLocation,
    deleteLocation,
    getLocationById,
    getLocationByCountryName,
    updateLocation,
)
from app.customExceptions import (
    LocationAlreadyExistsException,
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.auth.functions import logMethod


class LocationManager:
    def __init__(self, asyncSession: AsyncSession):
        self.dbSession = asyncSession

    @logMethod
    async def createLocation(self, countryName: str) -> LocationTable:
        """
        Create a new location with the given country name.
        
        Args:
            countryName (str): The name of the country for the new location.
            
        Returns:
            LocationTable: The created location.
            
        Raises:
            LocationAlreadyExistsException: If a location with the same country name already exists.
            LocationManagerException: If there's an error creating the location.
        """
        try:
            existingLocation = await getLocationByCountryName(self.dbSession, countryName)
            if existingLocation:
                raise LocationAlreadyExistsException(f"Location with country name '{countryName}' already exists")
            
            location = await createLocation(self.dbSession, countryName)
            await self.dbSession.commit()
            return location
        except IntegrityError as e:
            await self.dbSession.rollback()
            raise LocationAlreadyExistsException(f"Location with country name '{countryName}' already exists") from e
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationManagerException(f"Error creating location: {str(e)}") from e

    @logMethod
    async def updateLocation(self, locationId: int, newCountryName: str) -> LocationTable:
        """
        Update a location's country name.
        
        Args:
            locationId (int): The ID of the location to update.
            newCountryName (str): The new country name for the location.
            
        Returns:
            LocationTable: The updated location.
            
        Raises:
            LocationNotFoundException: If the location is not found.
            LocationUpdateError: If there's an error updating the location.
        """
        try:
            location = await updateLocation(self.dbSession, locationId, newCountryName)
            if not location:
                raise LocationNotFoundException(f"Location with ID {locationId} not found")
            
            await self.dbSession.commit()
            return location
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationUpdateError(f"Error updating location: {str(e)}") from e

    @logMethod
    async def deleteLocation(self, locationId: int) -> bool:
        """
        Delete a location by its ID.
        
        Args:
            locationId (int): The ID of the location to delete.
            
        Returns:
            bool: True if the location was deleted, False otherwise.
            
        Raises:
            LocationDeleteError: If there's an error deleting the location.
        """
        try:
            deleted = await deleteLocation(self.dbSession, locationId)
            if not deleted:
                raise LocationNotFoundException(f"Location with ID {locationId} not found")
            
            await self.dbSession.commit()
            return True
        except SQLAlchemyError as e:
            await self.dbSession.rollback()
            raise LocationDeleteError(f"Error deleting location: {str(e)}") from e

    @logMethod
    async def getLocation(self, locationId: int) -> LocationTable:
        """
        Get a location by its ID.
        
        Args:
            locationId (int): The ID of the location to retrieve.
            
        Returns:
            LocationTable: The requested location.
            
        Raises:
            LocationNotFoundException: If the location is not found.
        """
        location = await getLocationById(self.dbSession, locationId)
        if not location:
            raise LocationNotFoundException(f"Location with ID {locationId} not found")
        return location 

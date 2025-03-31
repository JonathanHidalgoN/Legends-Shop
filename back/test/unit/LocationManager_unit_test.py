import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.customExceptions import (
    LocationAlreadyExistsException,
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.location.LocationManager import LocationManager
from app.data.models.LocationTable import LocationTable
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def manager() -> LocationManager:
    mockSession = MagicMock(spec=AsyncSession)
    manager = LocationManager(mockSession)
    return manager


@pytest.mark.asyncio
async def test_createLocation_success(manager):
    countryName = "Test Country"
    mockLocation = LocationTable(id=1, country_name=countryName)
    
    with patch("app.location.LocationManager.getLocationByCountryName", new=AsyncMock(return_value=None)), \
         patch("app.location.LocationManager.createLocation", new=AsyncMock(return_value=mockLocation)):
        location = await manager.createLocation(countryName)
        assert location.id == 1
        assert location.country_name == countryName
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_createLocation_already_exists(manager):
    countryName = "Existing Country"
    mockLocation = LocationTable(id=1, country_name=countryName)
    
    with patch("app.location.LocationManager.getLocationByCountryName", new=AsyncMock(return_value=mockLocation)):
        with pytest.raises(LocationAlreadyExistsException):
            await manager.createLocation(countryName)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_createLocation_db_error(manager):
    countryName = "Test Country"
    
    with patch("app.location.LocationManager.getLocationByCountryName", new=AsyncMock(return_value=None)), \
         patch("app.location.LocationManager.createLocation", new=AsyncMock(side_effect=SQLAlchemyError("DB error"))):
        with pytest.raises(LocationManagerException):
            await manager.createLocation(countryName)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_updateLocation_success(manager):
    locationId = 1
    newCountryName = "Updated Country"
    mockLocation = LocationTable(id=locationId, country_name=newCountryName)
    
    with patch("app.location.LocationManager.updateLocation", new=AsyncMock(return_value=mockLocation)):
        location = await manager.updateLocation(locationId, newCountryName)
        assert location.id == locationId
        assert location.country_name == newCountryName
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_updateLocation_not_found(manager):
    locationId = 1
    newCountryName = "Updated Country"
    
    with patch("app.location.LocationManager.updateLocation", new=AsyncMock(return_value=None)):
        with pytest.raises(LocationNotFoundException):
            await manager.updateLocation(locationId, newCountryName)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_updateLocation_db_error(manager):
    locationId = 1
    newCountryName = "Updated Country"
    
    with patch("app.location.LocationManager.updateLocation", new=AsyncMock(side_effect=SQLAlchemyError("DB error"))):
        with pytest.raises(LocationUpdateError):
            await manager.updateLocation(locationId, newCountryName)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_deleteLocation_success(manager):
    locationId = 1
    
    with patch("app.location.LocationManager.deleteLocation", new=AsyncMock(return_value=True)):
        result = await manager.deleteLocation(locationId)
        assert result is True
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_deleteLocation_not_found(manager):
    locationId = 1
    
    with patch("app.location.LocationManager.deleteLocation", new=AsyncMock(return_value=False)):
        with pytest.raises(LocationNotFoundException):
            await manager.deleteLocation(locationId)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_deleteLocation_db_error(manager):
    locationId = 1
    
    with patch("app.location.LocationManager.deleteLocation", new=AsyncMock(side_effect=SQLAlchemyError("DB error"))):
        with pytest.raises(LocationDeleteError):
            await manager.deleteLocation(locationId)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_getLocation_success(manager):
    locationId = 1
    mockLocation = LocationTable(id=locationId, country_name="Test Country")
    
    with patch("app.location.LocationManager.getLocationById", new=AsyncMock(return_value=mockLocation)):
        location = await manager.getLocation(locationId)
        assert location.id == locationId
        assert location.country_name == "Test Country"


@pytest.mark.asyncio
async def test_getLocation_not_found(manager):
    locationId = 1
    
    with patch("app.location.LocationManager.getLocationById", new=AsyncMock(return_value=None)):
        with pytest.raises(LocationNotFoundException):
            await manager.getLocation(locationId) 

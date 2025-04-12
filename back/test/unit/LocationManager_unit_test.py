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
from app.schemas.Location import Location
from app.data.mappers import mapLocationTableToLocation
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def manager() -> LocationManager:
    mockSession = MagicMock(spec=AsyncSession)
    manager = LocationManager(mockSession)
    return manager


@pytest.mark.asyncio
async def test_createLocation_success(manager):
    countryName = "Test Country"

    with patch(
        "app.location.LocationManager.getLocationByCountryName",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.location.LocationManager.createLocation", new=AsyncMock(return_value=None)
    ):
        await manager.createLocation(countryName)
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_createLocation_already_exists(manager):
    countryName = "Existing Country"
    mockLocation = LocationTable(id=1, country_name=countryName)

    with patch(
        "app.location.LocationManager.getLocationByCountryName",
        new=AsyncMock(return_value=mockLocation),
    ):
        with pytest.raises(LocationAlreadyExistsException):
            await manager.createLocation(countryName)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_createLocation_db_error(manager):
    countryName = "Test Country"

    with patch(
        "app.location.LocationManager.getLocationByCountryName",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.location.LocationManager.createLocation",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(LocationManagerException):
            await manager.createLocation(countryName)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_updateLocation_success(manager):
    locationId = 1
    newCountryName = "Updated Country"
    mockLocation = LocationTable(id=locationId, country_name=newCountryName)

    with patch(
        "app.location.LocationManager.getLocationById",
        new=AsyncMock(return_value=mockLocation),
    ), patch(
        "app.location.LocationManager.updateLocation", new=AsyncMock(return_value=None)
    ):
        await manager.updateLocation(locationId, newCountryName)
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_updateLocation_not_found(manager):
    locationId = 1
    newCountryName = "Updated Country"

    with patch(
        "app.location.LocationManager.getLocationById", new=AsyncMock(return_value=None)
    ):
        with pytest.raises(LocationNotFoundException):
            await manager.updateLocation(locationId, newCountryName)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_updateLocation_db_error(manager):
    locationId = 1
    newCountryName = "Updated Country"
    mockLocation = LocationTable(id=locationId, country_name=newCountryName)

    with patch(
        "app.location.LocationManager.getLocationById",
        new=AsyncMock(return_value=mockLocation),
    ), patch(
        "app.location.LocationManager.updateLocation",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(LocationUpdateError):
            await manager.updateLocation(locationId, newCountryName)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_deleteLocation_success(manager):
    locationId = 1
    mockLocation = LocationTable(id=locationId, country_name="Test Country")

    with patch(
        "app.location.LocationManager.getLocationById",
        new=AsyncMock(return_value=mockLocation),
    ), patch(
        "app.location.LocationManager.deleteLocation", new=AsyncMock(return_value=None)
    ):
        await manager.deleteLocation(locationId)
        manager.dbSession.commit.assert_called_once()


@pytest.mark.asyncio
async def test_deleteLocation_not_found(manager):
    locationId = 1

    with patch(
        "app.location.LocationManager.getLocationById", new=AsyncMock(return_value=None)
    ):
        with pytest.raises(LocationNotFoundException):
            await manager.deleteLocation(locationId)
        manager.dbSession.commit.assert_not_called()


@pytest.mark.asyncio
async def test_deleteLocation_db_error(manager):
    locationId = 1
    mockLocation = LocationTable(id=locationId, country_name="Test Country")

    with patch(
        "app.location.LocationManager.getLocationById",
        new=AsyncMock(return_value=mockLocation),
    ), patch(
        "app.location.LocationManager.deleteLocation",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(LocationDeleteError):
            await manager.deleteLocation(locationId)
        manager.dbSession.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_getLocation_success(manager):
    locationId = 1
    mockLocationTable = LocationTable(id=locationId, country_name="Test Country")
    expectedLocation = mapLocationTableToLocation(mockLocationTable)

    with patch(
        "app.location.LocationManager.getLocationById",
        new=AsyncMock(return_value=mockLocationTable),
    ):
        location = await manager.getLocation(locationId)
        assert location.id == expectedLocation.id
        assert location.country_name == expectedLocation.country_name


@pytest.mark.asyncio
async def test_getLocation_not_found(manager):
    locationId = 1

    with patch(
        "app.location.LocationManager.getLocationById", new=AsyncMock(return_value=None)
    ):
        with pytest.raises(LocationNotFoundException):
            await manager.getLocation(locationId)


@pytest.mark.asyncio
async def test_getAllLocations_success(manager):
    mockLocationTables = [
        LocationTable(id=1, country_name="Country 1"),
        LocationTable(id=2, country_name="Country 2"),
        LocationTable(id=3, country_name="Country 3"),
    ]

    with patch(
        "app.location.LocationManager.getAllLocations",
        new=AsyncMock(return_value=mockLocationTables),
    ):
        locations = await manager.getAllLocations()
        assert len(locations) == 3
        assert all(isinstance(loc, Location) for loc in locations)
        assert locations[0].country_name == "Country 1"
        assert locations[1].country_name == "Country 2"
        assert locations[2].country_name == "Country 3"


@pytest.mark.asyncio
async def test_getAllLocations_empty(manager):
    with patch(
        "app.location.LocationManager.getAllLocations", new=AsyncMock(return_value=[])
    ):
        locations = await manager.getAllLocations()
        assert len(locations) == 0
        assert isinstance(locations, list)
        assert all(isinstance(loc, Location) for loc in locations)


@pytest.mark.asyncio
async def test_getAllLocations_db_error(manager):
    with patch(
        "app.location.LocationManager.getAllLocations",
        new=AsyncMock(side_effect=SQLAlchemyError("DB error")),
    ):
        with pytest.raises(LocationManagerException):
            await manager.getAllLocations()

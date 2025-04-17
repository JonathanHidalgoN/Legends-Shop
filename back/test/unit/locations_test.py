import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.customExceptions import (
    LocationAlreadyExistsException,
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.routes.auth import getUserIdFromName
from staticData import STATIC_LOCATION1, STATIC_LOCATION2


STATIC_LOCATIONS = [STATIC_LOCATION1, STATIC_LOCATION2]

client = TestClient(app)


async def fake_getUserIdFromName() -> int:
    return 1


app.dependency_overrides[getUserIdFromName] = fake_getUserIdFromName


@pytest.mark.asyncio
async def test_get_all_locations_success():
    """Test successful retrieval of all locations."""
    with patch(
        "app.location.LocationManager.LocationManager.getAllLocations",
        new=AsyncMock(return_value=STATIC_LOCATIONS),
    ):
        response = client.get("/locations/all")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["id"] == STATIC_LOCATION1.id
        assert response.json()[0]["country_name"] == STATIC_LOCATION1.country_name
        assert response.json()[1]["id"] == STATIC_LOCATION2.id
        assert response.json()[1]["country_name"] == STATIC_LOCATION2.country_name


@pytest.mark.asyncio
async def test_get_all_locations_error():
    """Test error handling when retrieving all locations fails."""
    with patch(
        "app.location.LocationManager.LocationManager.getAllLocations",
        new=AsyncMock(
            side_effect=LocationManagerException("Error retrieving locations")
        ),
    ):
        response = client.get("/locations/all")
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_user_location_success():
    """Test successful retrieval of user's location."""
    mockLocationTable = MagicMock()
    mockLocationTable.id = STATIC_LOCATION1.id
    mockLocationTable.country_name = STATIC_LOCATION1.country_name

    with patch(
        "app.routes.locations.getUserLocation",
        new=AsyncMock(return_value=mockLocationTable),
    ):
        with patch(
            "app.routes.locations.mapLocationTableToLocation",
            return_value=STATIC_LOCATION1,
        ):
            response = client.get("/locations/user")
            assert response.status_code == 200
            assert response.json()["id"] == STATIC_LOCATION1.id
            assert response.json()["country_name"] == STATIC_LOCATION1.country_name


@pytest.mark.asyncio
async def test_get_user_location_not_found():
    """Test error handling when user's location is not found."""
    with patch(
        "app.routes.locations.getUserLocation", new=AsyncMock(return_value=None)
    ):
        response = client.get("/locations/user")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_location_error():
    """Test error handling when retrieving user's location fails."""
    with patch(
        "app.routes.locations.getUserLocation",
        new=AsyncMock(side_effect=Exception("Database error")),
    ):
        response = client.get("/locations/user")
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_create_location_success():
    """Test successful creation of a location."""
    with patch(
        "app.routes.locations.LocationManager.createLocation",
        new=AsyncMock(return_value=None),
    ):
        response = client.post("/locations/create?countryName=Mexico")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_location_already_exists():
    """Test error handling when creating a location that already exists."""
    with patch(
        "app.location.LocationManager.LocationManager.createLocation",
        new=AsyncMock(
            side_effect=LocationAlreadyExistsException(
                "Location with country name 'Mexico' already exists"
            )
        ),
    ):
        response = client.post("/locations/create?countryName=Mexico")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_location_error():
    """Test error handling when creating a location fails."""
    with patch(
        "app.location.LocationManager.LocationManager.createLocation",
        new=AsyncMock(side_effect=LocationManagerException("Error creating location")),
    ):
        response = client.post("/locations/create?countryName=Mexico")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_location_success():
    """Test successful update of a location."""
    with patch(
        "app.location.LocationManager.LocationManager.updateLocation",
        new=AsyncMock(return_value=None),
    ):
        response = client.put("/locations/1/update?countryName=United Kingdom")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_location_not_found():
    """Test error handling when updating a location that doesn't exist."""
    with patch(
        "app.location.LocationManager.LocationManager.updateLocation",
        new=AsyncMock(
            side_effect=LocationNotFoundException("Location with ID 1 not found")
        ),
    ):
        response = client.put("/locations/1/update?countryName=United Kingdom")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_location_error():
    """Test error handling when updating a location fails."""
    with patch(
        "app.location.LocationManager.LocationManager.updateLocation",
        new=AsyncMock(side_effect=LocationUpdateError("Error updating location")),
    ):
        response = client.put("/locations/1/update?countryName=United Kingdom")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_location_success():
    """Test successful deletion of a location."""
    with patch(
        "app.location.LocationManager.LocationManager.deleteLocation",
        new=AsyncMock(return_value=None),
    ):
        response = client.delete("/locations/1")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_location_not_found():
    """Test error handling when deleting a location that doesn't exist."""
    with patch(
        "app.location.LocationManager.LocationManager.deleteLocation",
        new=AsyncMock(
            side_effect=LocationNotFoundException("Location with ID 1 not found")
        ),
    ):
        response = client.delete("/locations/1")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_location_error():
    """Test error handling when deleting a location fails."""
    with patch(
        "app.location.LocationManager.LocationManager.deleteLocation",
        new=AsyncMock(side_effect=LocationDeleteError("Error deleting location")),
    ):
        response = client.delete("/locations/1")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_location_success():
    """Test successful retrieval of a location by ID."""
    with patch(
        "app.location.LocationManager.LocationManager.getLocation",
        new=AsyncMock(return_value=STATIC_LOCATION1),
    ):
        response = client.get("/locations/1")
        assert response.status_code == 200
        assert response.json()["id"] == STATIC_LOCATION1.id
        assert response.json()["country_name"] == STATIC_LOCATION1.country_name


@pytest.mark.asyncio
async def test_get_location_not_found():
    """Test error handling when retrieving a location that doesn't exist."""
    with patch(
        "app.location.LocationManager.LocationManager.getLocation",
        new=AsyncMock(
            side_effect=LocationNotFoundException("Location with ID 1 not found")
        ),
    ):
        response = client.get("/locations/1")
        assert response.status_code == 404

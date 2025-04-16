from config import *
from app.data.models.UserTable import UserTable
from app.data.models.LocationTable import LocationTable
import pytest
from sqlalchemy import select
from datetime import date
from app.auth.functions import hashPassword


@pytest.mark.asyncio
async def testGetAllLocationsSuccess(client, dbSession):
    """Test successful retrieval of all locations."""
    # Setup test data
    location1 = LocationTable(country_name="Test Country 1")
    location2 = LocationTable(country_name="Test Country 2")
    dbSession.add(location1)
    dbSession.add(location2)
    await dbSession.commit()
    
    # Get all locations
    response = client.get("/locations/all")
    
    # Check response
    assert response.status_code == 200
    locations = response.json()
    assert len(locations) == 2
    assert any(l["country_name"] == "Test Country 1" for l in locations)
    assert any(l["country_name"] == "Test Country 2" for l in locations)


@pytest.mark.asyncio
async def testGetUserLocationSuccess(client, dbSession):
    """Test successful retrieval of user's location."""
    # Setup test data
    location = LocationTable(country_name="Test Country")
    dbSession.add(location)
    await dbSession.commit()
    
    # Create a test user
    testUser = UserTable(
        userName="testuser",
        password=hashPassword("TestPassword123!"),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=1000,
        email="test@example.com",
        birthdate=date(2000, 1, 1),
        location_id=location.id
    )
    dbSession.add(testUser)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies
    
    # Get user's location
    response = client.get("/locations/user")
    
    # Check response
    assert response.status_code == 200
    userLocation = response.json()
    assert userLocation["country_name"] == "Test Country"


@pytest.mark.asyncio
async def testGetLocationByIdSuccess(client, dbSession):
    """Test successful retrieval of location by ID."""
    # Setup test data
    location = LocationTable(country_name="Test Country")
    dbSession.add(location)
    await dbSession.commit()
    
    # Get location by ID
    response = client.get(f"/locations/{location.id}")
    
    # Check response
    assert response.status_code == 200
    locationData = response.json()
    assert locationData["country_name"] == "Test Country"


@pytest.mark.asyncio
async def testGetLocationByIdNotFound(client):
    """Test getting non-existent location by ID."""
    # Try to get non-existent location
    response = client.get("/locations/99999")
    
    # Check response
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def testGetUserLocationUnauthorized(client):
    """Test getting user location without authentication."""
    # Try to get user location without authentication
    response = client.get("/locations/user")
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def testCreateLocationSuccess(client, dbSession):
    """Test successful creation of a new location."""
    # Create a new location
    response = client.post("/locations/create?countryName=New Country")
    
    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Location created successfully"
    
    # Verify location was created in the database
    result = await dbSession.execute(
        select(LocationTable).where(LocationTable.country_name == "New Country")
    )
    location = result.scalar_one_or_none()
    assert location is not None
    assert location.country_name == "New Country"


@pytest.mark.asyncio
async def testUpdateLocationSuccess(client, dbSession):
    """Test successful update of a location."""
    # Setup test data
    location = LocationTable(country_name="Old Country")
    dbSession.add(location)
    await dbSession.commit()
    
    # Update the location
    response = client.put(
        f"/locations/{location.id}/update?countryName=Updated Country"
    )
    
    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Location updated successfully"
    
    # Verify location was updated in the database
    result = await dbSession.execute(
        select(LocationTable).where(LocationTable.id == location.id)
    )
    updatedLocation = result.scalar_one_or_none()
    assert updatedLocation is not None
    assert updatedLocation.country_name == "Updated Country"


@pytest.mark.asyncio
async def testDeleteLocationSuccess(client, dbSession):
    """Test successful deletion of a location."""
    # Setup test data
    location = LocationTable(country_name="Country to Delete")
    dbSession.add(location)
    await dbSession.commit()
    
    # Delete the location
    response = client.delete(f"/locations/{location.id}")
    
    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Location deleted successfully"
    
    # Verify location was deleted from the database
    result = await dbSession.execute(
        select(LocationTable).where(LocationTable.id == location.id)
    )
    deletedLocation = result.scalar_one_or_none()
    assert deletedLocation is None 
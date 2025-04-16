from config import *
from app.data.models.UserTable import UserTable
import pytest
from sqlalchemy import select
from datetime import date
from app.auth.functions import hashPassword


@pytest.mark.asyncio
async def testGetCurrentGoldSuccess(client, dbSession):
    """Test successful retrieval of user's current gold."""
    # Setup test data
    locationId:int = await addLocation(dbSession)
    
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
        location_id=locationId
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
    
    # Get user's current gold
    response = client.get("/profile/current_gold")
    
    # Check response
    assert response.status_code == 200
    assert response.json() == 1000


@pytest.mark.asyncio
async def testGetProfileInfoSuccess(client, dbSession):
    """Test successful retrieval of user's profile info."""
    # Setup test data
    locationId:int = await addLocation(dbSession)
    
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
        location_id=locationId
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
    
    # Get user's profile info
    response = client.get("/profile/info")
    
    # Check response
    assert response.status_code == 200
    profileInfo = response.json()
    assert profileInfo["user"]["userName"] == "testuser"
    assert profileInfo["user"]["email"] == "test@example.com"
    assert profileInfo["user"]["currentGold"] == 1000
    assert profileInfo["user"]["locationId"] == locationId


@pytest.mark.asyncio
async def testGetProfileInfoUnauthorized(client):
    """Test getting profile info without authentication."""
    # Try to get profile info without authentication
    response = client.get("/profile/info")
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def testGetCurrentGoldUnauthorized(client):
    """Test getting current gold without authentication."""
    # Try to get current gold without authentication
    response = client.get("/profile/current_gold")
    
    # Check response
    assert response.status_code == 401
    assert "detail" in response.json() 
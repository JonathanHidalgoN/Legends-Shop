from config import *
from app.data.models.UserTable import UserTable
import pytest
from sqlalchemy import text 
from datetime import date
from app.auth.functions import hashPassword

def test_get_home(client):
    """Test the home endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

def test_error_handling(client):
    """Test error handling for non-existent resources."""
    response = client.get("/users/99999")
    assert response.status_code == 404
    response = client.get("/items/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_signup_success(client, dbSession):
    """Test successful user signup."""
    # Test data
    test_signup_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
    }
    
    await addLocation(dbSession)
    response = client.post("/auth/singup", data=test_signup_data)
    assert response.status_code == 200
    assert response.json() == {"message": "nice"}
    result = await dbSession.execute(
        text("SELECT * FROM user_table WHERE userName = 'testuser'")
    )
    user = result.fetchone()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.location_id == 1

@pytest.mark.asyncio
async def test_signup_username_exists(client, dbSession):
    """Test signup with an existing username."""
    # Test data
    test_signup_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
    }
    
    await addLocation(dbSession)

    existingUser = UserTable(
        userName=test_signup_data["username"],
        password=hashPassword(test_signup_data["password"]),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=99999,
        email=test_signup_data["email"],
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existingUser)
    await dbSession.commit()

    response = client.post("/auth/singup", data=test_signup_data)
    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_email_exists(client, dbSession):
    """Test signup with an existing email."""
    # Test data
    test_signup_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
    }
    
    await addLocation(dbSession)

    existingUser = UserTable(
        userName="different_name",
        password=hashPassword("Password123!"),
        created=date.today(),
        last_singn=date.today(),
        gold_spend=0,
        current_gold=99999,
        email=test_signup_data["email"],
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existingUser)
    await dbSession.commit()

    response = client.post("/auth/singup", data=test_signup_data)

    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_invalid_location(client):
    """Test signup with an invalid location ID."""
    # Test data
    test_signup_data_invalid_location = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 32131231
    }
    
    response = client.post("/auth/singup", data=test_signup_data_invalid_location)
    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_login_flow(client, dbSession):
    """Test the complete signup and login flow."""
    # Test data
    test_signup_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
    }
    
    test_login_data = {
        "username": test_signup_data["username"],
        "password": test_signup_data["password"],
    }
    
    await addLocation(dbSession)
    signup_response = client.post("/auth/singup", data=test_signup_data)
    assert signup_response.status_code == 200
    login_response = client.post("/auth/token", data=test_login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

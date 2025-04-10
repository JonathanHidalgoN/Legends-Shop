import slowapi

#Hacky way of changing the limit function of slowapi, if they change the class 
#structure or limit signature this wont work, but for now is the best way I found to
#ignore the rate limiting, maybe when running test add an env variable and dynamically 
#set the limit
#TODO: env variable to change the limits in test mode
def fakeLimit(*args, **kwargs):
    def decorator(f):
        return f  
    return decorator

slowapi.Limiter.limit = fakeLimit

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date
from app.data.models.LocationTable import LocationTable
from app.data.models.UserTable import UserTable
from app.auth.functions import hashPassword

from app.main import app
from app.data.database import getDbSession


# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

# Create an async session factory
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def dbSession():
    """Create a test database session."""
    from app.data.database import base
    from app.data.models import (
        GoldTable,
        ItemTable,
        StatsTable,
        TagsTable,
        EffectsTable,
        MetaDataTable,
        UserTable,
        StatsMappingTable,
        OrderTable,
        CartTable,
        DeliveryDatesTable,
        LocationTable,
        ReviewTable,
    )

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)


@pytest_asyncio.fixture
def client(dbSession):
    async def fakeAsyncDb():
        return dbSession

    app.dependency_overrides[getDbSession] = fakeAsyncDb


    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


TEST_SINGUP_DATA = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
}
TEST_SINGUP_DATA_INVALID_LOCATION = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 32131231
}
TEST_LOGIN_DATA = {
    "username": TEST_SINGUP_DATA["username"],
    "password": TEST_SINGUP_DATA["password"],
}

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
    test_location = LocationTable(country_name="Test Country")
    dbSession.add(test_location)
    await dbSession.commit()
    response = client.post("/auth/singup", data=TEST_SINGUP_DATA)
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
    test_location = LocationTable(country_name="Test Country")
    dbSession.add(test_location)
    await dbSession.commit()

    existing_user = UserTable(
        userName=TEST_SINGUP_DATA["username"],
        password=hashPassword("Password123!"),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=99999,
        email="existing@example.com",
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existing_user)
    await dbSession.commit()

    response = client.post("/auth/singup", data=TEST_SINGUP_DATA)
    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_email_exists(client, dbSession):
    """Test signup with an existing email."""
    test_location = LocationTable(country_name="Test Country")
    dbSession.add(test_location)
    await dbSession.commit()

    existing_user = UserTable(
        userName="existinguser",
        password=hashPassword("Password123!"),
        created=date.today(),
        last_singn=date.today(),
        gold_spend=0,
        current_gold=99999,
        email=TEST_SINGUP_DATA["email"],
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existing_user)
    await dbSession.commit()

    response = client.post("/auth/singup", data=TEST_SINGUP_DATA)

    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_invalid_location(client):
    """Test signup with an invalid location ID."""
    response = client.post("/auth/singup", data=TEST_SINGUP_DATA_INVALID_LOCATION)
    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_login_flow(client, dbSession):
    """Test the complete signup and login flow."""
    test_location = LocationTable(country_name="Test Country")
    dbSession.add(test_location)
    await dbSession.commit()
    signup_response = client.post("/auth/singup", data=TEST_SINGUP_DATA)
    assert signup_response.status_code == 200
    login_response = client.post("/auth/token", data=TEST_LOGIN_DATA)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies


# @pytest.mark.asyncio
# async def test_temp(client, dbSession):
#     """Test the complete signup and login flow."""
#     test_location = LocationTable(country_name="Test Country")
#     dbSession.add(test_location)
#     await dbSession.commit()
#
#     signup_data = {
#         "username": "loginuser",
#         "password": "LoginPassword123!",
#         "email": "login@example.com",
#         "birthDate": "2000-01-01",
#         "location_id": 1
#     }
#     signup_response = client.post("/auth/singup", data=signup_data)
#     assert signup_response.status_code == 200
#
#     login_data = {
#         "username": "loginuser",
#         "password": "LoginPassword123!",
#         "grant_type": "password"
#     }
#     login_response = client.post("/auth/token", data=login_data)
#
#     assert login_response.status_code == 200
#
#     assert "access_token" in login_response.cookies
#     access_token = login_response.cookies["access_token"]
#
#     headers = {"Cookie": f"access_token={access_token}"}
#     profile_response = client.get("/profile", headers=headers)
#     assert profile_response.status_code == 200
#
#     user_id_response = client.get("/auth/user_id", headers=headers)
#     assert user_id_response.status_code == 200
#     user_id = user_id_response.json()
#
#     result = await dbSession.execute(
#         text("SELECT * FROM user_table WHERE userName = 'loginuser'")
#     )
#     user = result.fetchone()
#     assert user is not None
#     assert user.id == user_id

import pytest
from fastapi.testclient import TestClient
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
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create an async session factory
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    from app.data.database import base
    from app.data.models import (
        GoldTable, ItemTable, StatsTable, TagsTable, EffectsTable,
        MetaDataTable, UserTable, StatsMappingTable, OrderTable,
        CartTable, DeliveryDatesTable, LocationTable, ReviewTable
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)

@pytest.fixture
def client(db_session):
    """Create a test client with a test database session."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[getDbSession] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

def test_get_home(client):
    """Test the home endpoint."""
    response = client.get("/")
    assert response.status_code == 200

def test_error_handling(client):
    """Test error handling for non-existent resources."""
    response = client.get("/users/99999")
    assert response.status_code == 404
    response = client.get("/items/99999")
    assert response.status_code == 404

# @pytest.mark.asyncio
# async def test_signup_success(client, db_session):
#     """Test successful user signup."""
#     test_location = LocationTable(country_name="Test Country")
#     async for session in db_session:
#         session.add(test_location)
#         await session.commit()
#     test_data = {
#         "username": "testuser",
#         "password": "TestPassword123!",
#         "email": "test@example.com",
#         "birthDate": "2000-01-01",
#         "location_id": 1
#     }
#     response = client.post("/auth/singup", data=test_data)
#     assert response.status_code == 200
#     assert response.json() == {"message": "nice"}
#     async for session in db_session:
#         result = await session.execute(
#             "SELECT * FROM user_table WHERE userName = 'testuser'"
#         )
#         user = result.fetchone()
#         assert user is not None
#         assert user.email == "test@example.com"
#         assert user.location_id == 1

# @pytest.mark.asyncio
# async def test_signup_username_exists(client, db_session):
#     """Test signup with an existing username."""
#     # Create a test location
#     test_location = LocationTable(country_name="Test Country")
#     db_session.add(test_location)
#     await db_session.commit()
#
#     # Create a user first
#     existing_user = UserTable(
#         userName="existinguser",
#         password=hashPassword("Password123!"),
#         created=date.today(),
#         last_singn=date.today(),
#         gold_spend=0,
#         current_gold=99999,
#         email="existing@example.com",
#         birthdate=date(2000, 1, 1),
#         location_id=1
#     )
#     db_session.add(existing_user)
#     await db_session.commit()
#
#     # Try to sign up with the same username
#     test_data = {
#         "username": "existinguser",
#         "password": "TestPassword123!",
#         "email": "new@example.com",
#         "birthDate": "2000-01-01",
#         "location_id": 1
#     }
#
#     response = client.post("/auth/singup", data=test_data)
#
#     # Assert response
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Username exist, change it"
#     assert "X-Error-Type" in response.headers
#
# @pytest.mark.asyncio
# async def test_signup_email_exists(client, db_session):
#     """Test signup with an existing email."""
#     # Create a test location
#     test_location = LocationTable(country_name="Test Country")
#     db_session.add(test_location)
#     await db_session.commit()
#
#     # Create a user first
#     existing_user = UserTable(
#         userName="existinguser",
#         password=hashPassword("Password123!"),
#         created=date.today(),
#         last_singn=date.today(),
#         gold_spend=0,
#         current_gold=99999,
#         email="existing@example.com",
#         birthdate=date(2000, 1, 1),
#         location_id=1
#     )
#     db_session.add(existing_user)
#     await db_session.commit()
#
#     # Try to sign up with the same email
#     test_data = {
#         "username": "newuser",
#         "password": "TestPassword123!",
#         "email": "existing@example.com",
#         "birthDate": "2000-01-01",
#         "location_id": 1
#     }
#
#     response = client.post("/auth/singup", data=test_data)
#
#     # Assert response
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Email exist, change it"
#     assert "X-Error-Type" in response.headers
#
# @pytest.mark.asyncio
# async def test_signup_invalid_location(client, db_session):
#     """Test signup with an invalid location ID."""
#     # Test data with non-existent location ID
#     test_data = {
#         "username": "testuser",
#         "password": "TestPassword123!",
#         "email": "test@example.com",
#         "birthDate": "2000-01-01",
#         "location_id": 999  # Non-existent location ID
#     }
#
#     response = client.post("/auth/singup", data=test_data)
#
#     # Assert response
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Location does not exist"
#     assert "X-Error-Type" in response.headers

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

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.data.models.LocationTable import LocationTable

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


async def addLocation(dbSession):
    test_location = LocationTable(country_name="Test Country")
    dbSession.add(test_location)
    await dbSession.commit()

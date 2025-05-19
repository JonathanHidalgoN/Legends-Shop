import pytest_asyncio
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.data.models.LocationTable import LocationTable

from app.main import app
from app.data.database import getDbSession

# Mock ItemsLoader for testing
class MockItemsLoader:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.version = "test-version"

    async def updateItems(self) -> None:
        return

    async def getLastVersion(self) -> str:
        return self.version

# Mock SystemInitializer for testing
class MockSystemInitializer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.itemsLoader = MockItemsLoader(db)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def initializeSystem(self) -> None:
        return

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
    # Patch both SystemInitializer and ItemsLoader with our mock versions
    with patch('app.main.SystemInitializer', MockSystemInitializer), \
         patch('app.data.ItemsLoader.ItemsLoader', MockItemsLoader), \
         patch('app.routes.items.ItemsLoader', MockItemsLoader):
        
        async def fakeAsyncDb():
            return dbSession

        app.dependency_overrides[getDbSession] = fakeAsyncDb

        # Create test client with base_url to handle secure cookies
        with TestClient(app, base_url="https://testserver") as test_client:
            yield test_client

        app.dependency_overrides.clear()


async def addLocation(dbSession)->int:
    testLocation = LocationTable(country_name="Test Country")
    dbSession.add(testLocation)
    await dbSession.commit()
    return testLocation.id

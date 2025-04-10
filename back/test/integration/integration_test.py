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

from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from integrationStaticData import * 
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date
from app.data.models.LocationTable import LocationTable
from app.data.models.UserTable import UserTable
from app.auth.functions import hashPassword
from app.data.models.TagsTable import ItemTagsAssociation
from app.data.models.EffectsTable import EffectsTable, ItemEffectAssociation

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
    await addLocation(dbSession)
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
    await addLocation(dbSession)

    existingUser = UserTable(
        userName=TEST_SINGUP_DATA["username"],
        password=hashPassword(TEST_SINGUP_DATA["password"]),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=99999,
        email=TEST_SINGUP_DATA["email"],
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existingUser)
    await dbSession.commit()

    response = client.post("/auth/singup", data=TEST_SINGUP_DATA)
    assert response.status_code == 400
    assert "X-Error-Type" in response.headers

@pytest.mark.asyncio
async def test_signup_email_exists(client, dbSession):
    """Test signup with an existing email."""
    await addLocation(dbSession)

    existingUser = UserTable(
        userName="different_name",
        password=hashPassword("Password123!"),
        created=date.today(),
        last_singn=date.today(),
        gold_spend=0,
        current_gold=99999,
        email=TEST_SINGUP_DATA["email"],
        birthdate=date(2000, 1, 1),
        location_id=1
    )
    dbSession.add(existingUser)
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
    await addLocation(dbSession)
    signup_response = client.post("/auth/singup", data=TEST_SINGUP_DATA)
    assert signup_response.status_code == 200
    login_response = client.post("/auth/token", data=TEST_LOGIN_DATA)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

@pytest.mark.asyncio
async def test_get_unique_tags(client, dbSession):
    """Test the getUniqueTags endpoint."""
    dbSession.add(GOLD_TABLE_1)
    dbSession.add(GOLD_TABLE_2)
    await dbSession.commit()
    ITEM_TABLE_1.gold_id = GOLD_TABLE_1.id
    ITEM_TABLE_2.gold_id = GOLD_TABLE_2.id
    
    dbSession.add(ITEM_TABLE_1)
    dbSession.add(ITEM_TABLE_2)
    await dbSession.commit()
    
    dbSession.add(TAG_TABLE_1)
    dbSession.add(TAG_TABLE_2)
    dbSession.add(TAG_TABLE_3)
    await dbSession.commit()
    
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=ITEM_TABLE_1.id, tags_id=TAG_TABLE_1.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=ITEM_TABLE_1.id, tags_id=TAG_TABLE_2.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=ITEM_TABLE_2.id, tags_id=TAG_TABLE_2.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=ITEM_TABLE_2.id, tags_id=TAG_TABLE_3.id)
    )
    await dbSession.commit()
    
    response = client.get("/items/uniqueTags")
    
    assert response.status_code == 200
    tags = response.json()
    
    assert TAG_TABLE_1.name in tags
    assert TAG_TABLE_2.name in tags
    assert TAG_TABLE_3.name in tags
    
    assert len(tags) == 3
    
    assert len(set(tags)) == 3

@pytest.mark.asyncio
async def test_get_item_names(client, dbSession):
    """Test the item_names endpoint."""
    gold1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    response = client.get("/items/item_names")
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 200
    item_names = response.json()
    
    assert "Test Item 1" in item_names
    assert "Test Item 2" in item_names
    
    assert len(item_names) == 2
    
    assert len(set(item_names)) == 2

@pytest.mark.asyncio
async def test_get_unique_effects(client, dbSession):
    """Test the unique_effects endpoint."""
    gold1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    effect1 = EffectsTable(name="Effect 1")
    effect2 = EffectsTable(name="Effect 2")
    effect3 = EffectsTable(name="Effect 3")
    dbSession.add(effect1)
    dbSession.add(effect2)
    dbSession.add(effect3)
    await dbSession.commit()
    
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect1.id, value=10.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect2.id, value=20.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect2.id, value=30.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect3.id, value=40.0)
    )
    await dbSession.commit()
    
    response = client.get("/items/unique_effects")
    
    assert response.status_code == 200
    effects = response.json()
    
    assert "Effect 1" in effects
    assert "Effect 2" in effects
    assert "Effect 3" in effects
    
    assert len(effects) == 3
    
    assert len(set(effects)) == 3

@pytest.mark.asyncio
async def test_get_all_items(client, dbSession):
    """Test the /items/all endpoint."""
    # Create gold records first
    gold1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    # Create test items with references to gold records
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    # Create test tags
    tag1 = TagsTable(name="Tag1")
    tag2 = TagsTable(name="Tag2")
    dbSession.add(tag1)
    dbSession.add(tag2)
    await dbSession.commit()
    
    # Create item-tag associations
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item1.id, tags_id=tag1.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item2.id, tags_id=tag2.id)
    )
    await dbSession.commit()
    
    # Create test effects
    effect1 = EffectsTable(name="Effect1")
    effect2 = EffectsTable(name="Effect2")
    dbSession.add(effect1)
    dbSession.add(effect2)
    await dbSession.commit()
    
    # Create item-effect associations
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect1.id, value=10.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect2.id, value=20.0)
    )
    await dbSession.commit()
    
    # Create test stats
    stat1 = StatsTable(name="Stat1", kind="flat")
    stat2 = StatsTable(name="Stat2", kind="percentage")
    dbSession.add(stat1)
    dbSession.add(stat2)
    await dbSession.commit()
    
    # Create item-stat associations
    await dbSession.execute(
        insert(ItemStatAssociation).values(item_id=item1.id, stat_id=stat1.id, value=5.0)
    )
    await dbSession.execute(
        insert(ItemStatAssociation).values(item_id=item2.id, stat_id=stat2.id, value=15.0)
    )
    await dbSession.commit()
    
    # Call the endpoint
    response = client.get("/items/all")
    
    # Verify the response
    assert response.status_code == 200
    items = response.json()
    
    # Check that we got the expected number of items
    assert len(items) == 2
    
    # Check the first item
    item1_response = next((item for item in items if item["name"] == "Test Item 1"), None)
    assert item1_response is not None
    assert item1_response["plaintext"] == "Plain text for test item 1"
    assert item1_response["description"] == "Description for test item 1"
    assert item1_response["image"] == "item1.jpg"
    assert item1_response["imageUrl"] == "http://example.com/item1.jpg"
    assert item1_response["id"] == item1.id
    
    # Check gold for the first item
    assert item1_response["gold"]["base"] == 100
    assert item1_response["gold"]["total"] == 100
    assert item1_response["gold"]["sell"] == 70
    assert item1_response["gold"]["purchasable"] is True
    
    # Check tags for the first item
    assert "Tag1" in item1_response["tags"]
    assert len(item1_response["tags"]) == 1
    
    # Check effects for the first item
    assert "Effect1" in item1_response["effect"]
    assert item1_response["effect"]["Effect1"] == 10.0
    assert len(item1_response["effect"]) == 1
    
    # Check stats for the first item
    stat1_response = next((stat for stat in item1_response["stats"] if stat["name"] == "Stat1"), None)
    assert stat1_response is not None
    assert stat1_response["kind"] == "flat"
    assert stat1_response["value"] == 5.0
    assert len(item1_response["stats"]) == 1
    
    # Check the second item
    item2_response = next((item for item in items if item["name"] == "Test Item 2"), None)
    assert item2_response is not None
    assert item2_response["plaintext"] == "Plain text for test item 2"
    assert item2_response["description"] == "Description for test item 2"
    assert item2_response["image"] == "item2.jpg"
    assert item2_response["imageUrl"] == "http://example.com/item2.jpg"
    assert item2_response["id"] == item2.id
    
    # Check gold for the second item
    assert item2_response["gold"]["base"] == 200
    assert item2_response["gold"]["total"] == 200
    assert item2_response["gold"]["sell"] == 140
    assert item2_response["gold"]["purchasable"] is True
    
    # Check tags for the second item
    assert "Tag2" in item2_response["tags"]
    assert len(item2_response["tags"]) == 1
    
    # Check effects for the second item
    assert "Effect2" in item2_response["effect"]
    assert item2_response["effect"]["Effect2"] == 20.0
    assert len(item2_response["effect"]) == 1
    
    # Check stats for the second item
    stat2_response = next((stat for stat in item2_response["stats"] if stat["name"] == "Stat2"), None)
    assert stat2_response is not None
    assert stat2_response["kind"] == "percentage"
    assert stat2_response["value"] == 15.0
    assert len(item2_response["stats"]) == 1

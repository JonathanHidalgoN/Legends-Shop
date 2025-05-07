from config import *
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.CartTable import CartTable
from app.schemas.Order import CartItem, CartStatus
import pytest
from sqlalchemy import select
from datetime import date
from app.auth.functions import hashPassword

@pytest.mark.asyncio
async def test_add_items_to_cart_success(client, dbSession):
    """Test successful addition of multiple items to cart."""
    # Setup test data
    locationId:int = await addLocation(dbSession)
    #
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

    # Create test items
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

    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies

    # Create cart items data
    cartItems = [
        CartItem(id=None,itemId=item1.id, status=CartStatus.ADDED),
        CartItem(id=None,itemId=item2.id, status=CartStatus.ADDED)
    ]

    response = client.post(
        "/cart/add_items", 
        json=[item.model_dump() for item in cartItems],
    )

    # Check response
    assert response.status_code == 200
    cartItemsResponse = response.json()
    assert len(cartItemsResponse) == 2

    # Verify cart items were created in the database
    result = await dbSession.execute(
        select(CartTable).where(CartTable.user_id == testUser.id)
    )
    cartItemsDb = result.scalars().all()
    assert len(cartItemsDb) == 2
    assert any(item.item_id == item1.id and item.status == CartStatus.ADDED for item in cartItemsDb)
    assert any(item.item_id == item2.id and item.status == CartStatus.ADDED for item in cartItemsDb)
    assert(1==1)


@pytest.mark.asyncio
async def test_get_cart_items_success(client, dbSession):
    """Test successful retrieval of cart items."""
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
    
    # Create test item
    gold = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    dbSession.add(gold)
    await dbSession.commit()
    
    item = ItemTable(
        name="Test Item",
        plain_text="Plain text for test item",
        description="Description for test item",
        image="item.jpg",
        imageUrl="http://example.com/item.jpg",
        updated=False,
        gold_id=gold.id
    )
    dbSession.add(item)
    await dbSession.commit()
    
    # Create cart item directly in database
    cartItem = CartTable(
        user_id=testUser.id,
        item_id=item.id,
        status=CartStatus.ADDED
    )
    dbSession.add(cartItem)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies
    
    # Get cart items
    response = client.get("/cart/added_cart_items")
    
    # Check response
    assert response.status_code == 200
    cartItems = response.json()
    assert len(cartItems) == 1
    assert cartItems[0]["itemId"] == item.id
    assert cartItems[0]["status"] == CartStatus.ADDED


@pytest.mark.asyncio
async def test_delete_cart_item_success(client, dbSession):
    """Test successful deletion of a cart item."""
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
    
    # Create test item
    gold = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    dbSession.add(gold)
    await dbSession.commit()
    
    item = ItemTable(
        name="Test Item",
        plain_text="Plain text for test item",
        description="Description for test item",
        image="item.jpg",
        imageUrl="http://example.com/item.jpg",
        updated=False,
        gold_id=gold.id
    )
    dbSession.add(item)
    await dbSession.commit()
    
    # Create cart item directly in database
    cart_item = CartTable(
        user_id=testUser.id,
        item_id=item.id,
        status=CartStatus.ADDED
    )
    dbSession.add(cart_item)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    login_response = client.post("/auth/token", data=loginData)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    
    # Delete cart item
    response = client.delete(f"/cart/delete_cart_item/{cart_item.id}")
    
    # Check response
    assert response.status_code == 200
    
    # Verify cart item status was changed to DELETED
    result = await dbSession.execute(
        select(CartTable).where(CartTable.id == cart_item.id)
    )
    deletedItem = result.scalar_one_or_none()
    assert deletedItem is not None
    assert deletedItem.status == CartStatus.DELETED 

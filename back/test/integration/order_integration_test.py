from config import *
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.DeliveryDatesTable import ItemLocationDeliveryAssociation
from app.data.models.OrderTable import OrderTable, OrderItemAssociation
from app.schemas.Order import OrderStatus
import pytest
from sqlalchemy import  select
from datetime import date, timedelta
from app.auth.functions import hashPassword


@pytest.mark.asyncio
async def test_create_order_success(client, dbSession):
    """Test successful order creation."""
    # Setup test data
    
    locationId:int = await addLocation(dbSession)
    
    # Create a test user
    test_user = UserTable(
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
    dbSession.add(test_user)
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
    
    # Create delivery dates
    today = date.today()
    delivery_date1 = ItemLocationDeliveryAssociation.insert().values(
        item_id=item1.id,
        location_id=locationId,
        days_plus=3
    )
    delivery_date2 = ItemLocationDeliveryAssociation.insert().values(
        item_id=item2.id,
        location_id=locationId,
        days_plus=5
    )
    await dbSession.execute(delivery_date1)
    await dbSession.execute(delivery_date2)
    await dbSession.commit()
    
    # Login to get authentication token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    login_response = client.post("/auth/token", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies
    
    # Create order data
    order_data = {
        "id": 0,  # This will be assigned by the server
        "itemNames": ["Test Item 1", "Test Item 2"],
        "userName": "testuser",
        "total": 300,  # 100 + 200
        "orderDate": today.isoformat(),
        "deliveryDate": (today + timedelta(days=5)).isoformat(),
        "status": OrderStatus.PENDING,
        "location_id": locationId,
        "reviewed": False
    }
    
    # Make the order request
    response = client.post("/orders/order", json=order_data)
    
    # Check response
    assert response.status_code == 200
    order_id = response.json()
    assert isinstance(order_id, int)
    assert order_id > 0

    # Verify order was created in the database
    result = await dbSession.execute(
        select(OrderTable).where(OrderTable.id == order_id)
    )
    order = result.scalar_one_or_none()
    assert order is not None
    assert order.user_id == test_user.id
    assert order.total == 300
    assert order.status == OrderStatus.PENDING
    assert order.location_id == 1

    # Verify order items were created
    result = await dbSession.execute(
        select(OrderItemAssociation).where(OrderItemAssociation.c.order_id == order_id)
    )
    order_items = result.scalars().all()
    assert len(order_items) == 2

    # Verify user's gold was updated
    result = await dbSession.execute(
        select(UserTable).where(UserTable.id == test_user.id)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.current_gold == 700  # 1000 - 300


@pytest.mark.asyncio
async def test_get_order_history(client, dbSession):
    """Test getting order history for a user."""
    # Setup test data
    locationId:int = await addLocation(dbSession)

    # Create a test user
    test_user = UserTable(
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
    dbSession.add(test_user)
    await dbSession.commit()

    # Create test items
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

    # Create delivery date
    today = date.today()
    delivery_date = ItemLocationDeliveryAssociation.insert().values(
        item_id=item.id,
        location_id=locationId,
        days_plus=3
    )
    await dbSession.execute(delivery_date)
    await dbSession.commit()

    # Create an order directly in the database
    order = OrderTable(
        user_id=test_user.id,
        total=100,
        order_date=today,
        delivery_date=today + timedelta(days=3),
        status=OrderStatus.PENDING,
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order)
    await dbSession.commit()

    # Create order item association
    await dbSession.execute(
        OrderItemAssociation.insert().values(
            order_id=order.id,
            item_id=item.id,
            quantity=1
        )
    )
    await dbSession.commit()

     # Login to get authentication token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    login_response = client.post("/auth/token", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

    # Get order history
    response = client.get("/orders/order_history")

    # Check response
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order.id
    assert orders[0]["total"] == 100
    assert orders[0]["status"] == OrderStatus.PENDING
    assert orders[0]["location_id"] == locationId
    assert "Test Item" in orders[0]["itemNames"]


@pytest.mark.asyncio
async def test_cancel_order(client, dbSession):
    """Test canceling an order."""
    # Setup test data
    locationId:int = await addLocation(dbSession)

    # Create a test user
    test_user = UserTable(
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
    dbSession.add(test_user)
    await dbSession.commit()

    # Create test items
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

    # Create delivery date
    today = date.today()
    delivery_date = ItemLocationDeliveryAssociation.insert().values(
        item_id=item.id,
        location_id=locationId,
        days_plus=3
    )
    await dbSession.execute(delivery_date)
    await dbSession.commit()

    # Create an order directly in the database
    order = OrderTable(
        user_id=test_user.id,
        total=100,
        order_date=today,
        delivery_date=today + timedelta(days=3),
        status=OrderStatus.PENDING,
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order)
    await dbSession.commit()

    # Create order item association
    await dbSession.execute(
        OrderItemAssociation.insert().values(
            order_id=order.id,
            item_id=item.id,
            quantity=1
        )
    )
    await dbSession.commit()

    # Login to get authentication token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    login_response = client.post("/auth/token", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

    # Cancel the order
    response = client.put(f"/orders/cancel_order/{order.id}")

    # Check response
    assert response.status_code == 200

    # Verify order was canceled in the database
    result = await dbSession.execute(
        select(OrderTable).where(OrderTable.id == order.id)
    )
    order = result.scalar_one_or_none()
    assert order is not None
    assert order.status == OrderStatus.CANCELED

    # Verify user's gold was refunded
    result = await dbSession.execute(
        select(UserTable).where(UserTable.id == test_user.id)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.current_gold == 1000  # Should be refunded to original amount


@pytest.mark.asyncio
async def test_order_insufficient_gold(client, dbSession):
    """Test order creation with insufficient gold."""
    # Setup test data
    locationId:int = await addLocation(dbSession)

    # Create a test user with low gold
    test_user = UserTable(
        userName="testuser",
        password=hashPassword("TestPassword123!"),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=50,  # Not enough for the order
        email="test@example.com",
        birthdate=date(2000, 1, 1),
        location_id=locationId
    )
    dbSession.add(test_user)
    await dbSession.commit()

    # Create test items
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

    # Create delivery date
    today = date.today()
    delivery_date = ItemLocationDeliveryAssociation.insert().values(
        item_id=item.id,
        location_id=locationId,
        days_plus=3
    )
    await dbSession.execute(delivery_date)
    await dbSession.commit()

    # Login to get authentication token
    login_data = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    login_response = client.post("/auth/token", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

    # Create order data
    order_data = {
        "id": 0,
        "itemNames": ["Test Item"],
        "userName": "testuser",
        "total": 100,
        "orderDate": today.isoformat(),
        "deliveryDate": (today + timedelta(days=3)).isoformat(),
        "status": OrderStatus.PENDING,
        "location_id": locationId,
        "reviewed": False
    }

    # Make the order request
    response = client.post("/orders/order", json=order_data)

    # Check response
    assert response.status_code == 400
    #
    # # Verify user's gold was not changed
    # result = await dbSession.execute(
    #     select(UserTable).where(UserTable.id == test_user.id)
    # )
    # user = result.scalar_one_or_none()
    # assert user is not None
    # assert user.current_gold == 50

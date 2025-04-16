from config import *
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.GoldTable import GoldTable
from app.data.models.OrderTable import OrderTable
from app.data.models.ReviewTable import ReviewTable
from app.schemas.Review import Review, Comment
import pytest
from sqlalchemy import select
from datetime import date, datetime
from app.auth.functions import hashPassword


@pytest.mark.asyncio
async def testAddReviewSuccess(client, dbSession):
    """Test successful addition of a review."""
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
    
    # Create an order for the user
    order = OrderTable(
        user_id=testUser.id,
        total=100,
        order_date=date.today(),
        delivery_date=date.today(),
        status="COMPLETED",
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies
    
    # Create review data
    reviewData = {
        "id": 0,  # Will be assigned by the server
        "orderId": order.id,
        "itemId": item.id,
        "rating": 5,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "comments": [
            {
                "id": 0,  # Will be assigned by the server
                "reviewId": 0,  # Will be assigned by the server
                "userId": testUser.id,
                "content": "Great product!",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
        ]
    }
    
    # Make the review request
    response = client.post("/review/add", json=reviewData)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Review added successfully"
    
    # Verify review was created in the database
    result = await dbSession.execute(
        select(ReviewTable).where(ReviewTable.order_id == order.id)
    )
    review = result.scalar_one_or_none()
    assert review is not None
    assert review.rating == 5
    assert review.item_id == item.id


@pytest.mark.asyncio
async def testUpdateReviewSuccess(client, dbSession):
    """Test successful update of a review."""
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
    
    # Create an order for the user
    order = OrderTable(
        user_id=testUser.id,
        total=100,
        order_date=date.today(),
        delivery_date=date.today(),
        status="COMPLETED",
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order)
    await dbSession.commit()
    
    # Create initial review
    review = ReviewTable(
        order_id=order.id,
        item_id=item.id,
        rating=3
    )
    dbSession.add(review)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies
    
    # Create updated review data
    updatedReviewData = {
        "id": review.id,
        "orderId": order.id,
        "itemId": item.id,
        "rating": 5,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "comments": [
            {
                "id": 0,  # Will be assigned by the server
                "reviewId": review.id,
                "userId": testUser.id,
                "content": "Changed my mind, it's actually great!",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
        ]
    }
    
    # Make the update request
    response = client.put("/review/update", json=updatedReviewData)
    
    # Check response
    assert response.status_code == 200
    assert response.json()["message"] == "Review updated successfully"
    
    # Verify review was updated in the database
    result = await dbSession.execute(
        select(ReviewTable).where(ReviewTable.id == review.id)
    )
    updatedReview = result.scalar_one_or_none()
    assert updatedReview is not None
    assert updatedReview.rating == 5


@pytest.mark.asyncio
async def testGetUserReviewsSuccess(client, dbSession):
    """Test successful retrieval of user's reviews."""
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
    
    # Create an order for the user
    order = OrderTable(
        user_id=testUser.id,
        total=100,
        order_date=date.today(),
        delivery_date=date.today(),
        status="COMPLETED",
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order)
    await dbSession.commit()
    
    # Create a review
    review = ReviewTable(
        order_id=order.id,
        item_id=item.id,
        rating=5
    )
    dbSession.add(review)
    await dbSession.commit()
    
    # Login to get authentication token
    loginData = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    loginResponse = client.post("/auth/token", data=loginData)
    assert loginResponse.status_code == 200
    assert "access_token" in loginResponse.cookies
    
    # Get user's reviews
    response = client.get("/review/user")
    
    # Check response
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 1
    assert reviews[0]["rating"] == 5
    assert reviews[0]["itemId"] == item.id


@pytest.mark.asyncio
async def testGetItemReviewsSuccess(client, dbSession):
    """Test successful retrieval of item's reviews."""
    # Setup test data
    locationId:int = await addLocation(dbSession)
    
    # Create test users
    testUser1 = UserTable(
        userName="testuser1",
        password=hashPassword("TestPassword123!"),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=1000,
        email="test1@example.com",
        birthdate=date(2000, 1, 1),
        location_id=locationId
    )
    testUser2 = UserTable(
        userName="testuser2",
        password=hashPassword("TestPassword123!"),
        gold_spend=0,
        created=date.today(),
        last_singn=date.today(),
        current_gold=1000,
        email="test2@example.com",
        birthdate=date(2000, 1, 1),
        location_id=locationId
    )
    dbSession.add(testUser1)
    dbSession.add(testUser2)
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
    
    # Create orders for both users
    order1 = OrderTable(
        user_id=testUser1.id,
        total=100,
        order_date=date.today(),
        delivery_date=date.today(),
        status="COMPLETED",
        location_id=locationId,
        reviewed=False
    )
    order2 = OrderTable(
        user_id=testUser2.id,
        total=100,
        order_date=date.today(),
        delivery_date=date.today(),
        status="COMPLETED",
        location_id=locationId,
        reviewed=False
    )
    dbSession.add(order1)
    dbSession.add(order2)
    await dbSession.commit()
    
    # Create reviews for the item
    review1 = ReviewTable(
        order_id=order1.id,
        item_id=item.id,
        rating=5
    )
    review2 = ReviewTable(
        order_id=order2.id,
        item_id=item.id,
        rating=4
    )
    dbSession.add(review1)
    dbSession.add(review2)
    await dbSession.commit()
    
    # Get item reviews (no authentication required)
    response = client.get(f"/review/item/{item.id}")
    
    # Check response
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 2
    assert any(r["rating"] == 5 for r in reviews)
    assert any(r["rating"] == 4 for r in reviews) 
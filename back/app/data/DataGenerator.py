from typing import List
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
import random
from datetime import date, timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.Item import Item
from app.data.mappers import mapOrderToOrderTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.data.queries.authQueries import insertUser, checkUserExistInDB
from app.data.queries.locationQueries import createLocation
from app.data.queries.reviewQueries import addReview, addComment
from app.data.queries.metaDataQueries import addMetaData, getMetaData
from app.schemas.Order import Order, OrderStatus
from app.schemas.AuthSchemas import UserInDB
from app.customExceptions import (
    LocationGenerationError,
    UserGenerationError,
    OrderGenerationError,
    OrderItemAssociationError,
    ReviewGenerationError,
    CommentGenerationError,
    DataGeneratorException
)
from app.logger import logMethod

class DataGenerator:
    def __init__(self, dbSession: AsyncSession, items:List[Item]):
        self.dbSession = dbSession
        self.items = items
        self.itemIds = [item.id for item in items]
        self.locationIds = []
        self.userIds = []
        self.orderIds = []

    @logMethod
    async def insertDummyLocations(self):
        try:
            locations : List[str] = ["Mexico","Korea","Japan","China","USA"]
            locationId = 1
            for location in locations:
                await createLocation(self.dbSession, location)
                self.locationIds.append(locationId)
                locationId +=1
        except SQLAlchemyError as e:
            raise LocationGenerationError(f"Failed to generate locations: {str(e)}") from e

    @logMethod
    async def insertFakeUsers(self):
        try:
            users: List[UserInDB] = [
                UserInDB(
                    userName="testuser1",
                    email="test1@example.com",
                    created=date.today() - timedelta(days=30),
                    lastSingIn=date.today(),
                    goldSpend=1000,
                    currentGold=500,
                    birthDate=date(1990, 1, 1),
                    hashedPassword="TestPassword123!",
                    locationId=1
                ),
                UserInDB(
                    userName="testuser2",
                    email="test2@example.com",
                    created=date.today() - timedelta(days=15),
                    lastSingIn=date.today(),
                    goldSpend=500,
                    currentGold=1000,
                    birthDate=date(1995, 5, 5),
                    hashedPassword="TestPassword456!",
                    locationId=2
                ),
                UserInDB(
                    userName="testuser3",
                    email="test3@example.com",
                    created=date.today() - timedelta(days=7),
                    lastSingIn=date.today(),
                    goldSpend=2000,
                    currentGold=300,
                    birthDate=date(1985, 10, 10),
                    hashedPassword="TestPassword789!",
                    locationId=3
                )
            ]
            userId = 1 
            for user in users:
                if not await checkUserExistInDB(self.dbSession, user.userName):
                    await insertUser(self.dbSession, user)
                    self.userIds.append(userId)
                userId += 1
        except SQLAlchemyError as e:
            raise UserGenerationError(f"Failed to generate users: {str(e)}") from e

    def popRandom(self, arg):
        return arg.pop(random.randrange(len(arg)))

    @logMethod
    async def insertFakeOrders(self):
        try:
            orderId = 1
            statuses = list(OrderStatus)
            now = datetime.now()
            for _ in range(100):
                orderDate = now - timedelta(days=random.randint(0, 30))
                deliveryDate = orderDate + timedelta(days=random.randint(1, 7))
                numItems = random.randint(1, 5)
                itemNames = [f"Item {random.randint(1, 100)}" for _ in range(numItems)]
                total = random.randint(100, 5000)
                status = random.choice(statuses)
                userId = random.choice(self.userIds)
                locationId = random.choice(self.locationIds)
                order = Order(
                    id=orderId,
                    itemNames=itemNames,
                    userName=f"testuser{userId}",
                    total=total,
                    orderDate=orderDate,
                    deliveryDate=deliveryDate,
                    status=status,
                    location_id=locationId,
                    reviewed=random.choice([True, False])
                )
                
                row: OrderTable = mapOrderToOrderTable(order, userId)
                self.dbSession.add(row)
                await self.dbSession.flush()
                self.orderIds.append(orderId)
                orderId += 1
        except SQLAlchemyError as e:
            raise OrderGenerationError(f"Failed to generate orders: {str(e)}") from e

    @logMethod
    async def insertFakeOrderItemAssociation(self):
        try:
            for orderId in self.orderIds:
                numberOfItemsInOrder = random.randint(1, 5)
                availableItemIds = self.itemIds.copy()
                for _ in range(numberOfItemsInOrder):
                    if not availableItemIds:
                        break
                    randomItemId = self.popRandom(availableItemIds)
                    quantity = random.randint(1, 10)
                    record = {
                        "order_id": orderId,
                        "item_id": randomItemId,
                        "quantity": quantity,
                    }
                    ins = insert(OrderItemAssociation).values(**record)
                    await self.dbSession.execute(ins)
        except SQLAlchemyError as e:
            raise OrderItemAssociationError(f"Failed to generate order-item associations: {str(e)}") from e

    @logMethod
    async def insertFakeReviewsAndComments(self):
        try:
            for _ in range(500):
                orderId = random.choice(self.orderIds)
                userId = random.choice(self.userIds)
                
                orderItems = await self.dbSession.execute(
                    select(OrderItemAssociation).where(OrderItemAssociation.c.order_id == orderId)
                )
                orderItems = list(orderItems.scalars().all())
                if not orderItems:
                    continue
                itemId = random.choice(orderItems).item_id
                rating = random.randint(1, 5)
                
                try:
                    reviewId = await addReview(
                        self.dbSession,
                        order_id=orderId,
                        item_id=itemId,
                        rating=rating
                    )
                except SQLAlchemyError as e:
                    raise ReviewGenerationError(f"Failed to generate review: {str(e)}") from e
                
                if random.random() < 0.7:
                    comments = [
                        "Great product, would buy again!",  # Positive feedback, indicates satisfaction
                        "Not as expected, but still good",  # Mixed feedback, some disappointment but overall positive
                        "Perfect for my needs",  # Positive feedback, directly addresses utility
                        "Could be better",  # Negative feedback, vague but indicates room for improvement
                        "Excellent quality",  # Positive feedback, highlights a key attribute
                        "Fast delivery",  # Positive feedback, relates to the service aspect
                        "Good value for money",  # Positive feedback, balances cost and quality
                        "Not worth the price",  # Negative feedback, directly criticizes the cost
                        "Exactly what I needed",  # Positive feedback, emphasizes meeting requirements
                        "Better than expected",  # Very positive feedback, exceeding initial thoughts
                        "Amazing!",  # Enthusiastic positive feedback
                        "Disappointed with the purchase",  # Strong negative feedback
                        "Easy to use",  # Positive feedback, focuses on usability
                        "Difficult to set up",  # Negative feedback, points out a usability issue
                        "Highly recommend",  # Strong positive endorsement
                        "Would not recommend",  # Strong negative discouragement
                        "The best I've ever used",  # Top-tier positive feedback
                        "The worst experience",  # Extremely negative feedback
                        "Met all my expectations",  # Positive feedback, confirms fulfillment
                        "Fell short of expectations",  # Negative feedback, indicates unmet needs
                        "Love it!",  # Simple and strong positive feedback
                        "Hate it!",  # Simple and strong negative feedback
                        "Works perfectly",  # Positive feedback, focuses on functionality
                        "Doesn't work as advertised",  # Negative feedback, criticizes functionality claims
                        "Great customer service",  # Positive feedback, highlights support
                        "Poor customer service",  # Negative feedback, criticizes support
                        "A fantastic buy!",  # Positive feedback, emphasizes the purchase decision
                        "A complete waste of money",  # Negative feedback, strong financial criticism
                        "So happy with this!",  # Expresses strong positive emotion
                        "Regret buying this",  # Expresses negative sentiment about the purchase
                        "Solid performance",  # Positive feedback, focuses on how it functions
                        "Unreliable",  # Negative feedback, criticizes dependability
                        "Well-designed",  # Positive feedback, comments on the aesthetics or structure
                        "Poorly designed",  # Negative feedback, criticizes the aesthetics or structure
                        "A must-have!",  # Strong positive recommendation
                        "Avoid at all costs!",  # Strong negative warning
                        "Incredible features",  # Positive feedback, highlights capabilities
                        "Lacking in features",  # Negative feedback, points out missing capabilities
                        "Durable and long-lasting",  # Positive feedback, focuses on longevity
                        "Broke after only a short time",  # Negative feedback, criticizes durability
                        "Simple and effective",  # Positive feedback, highlights ease and efficiency
                        "Complicated and inefficient",  # Negative feedback, criticizes complexity and performance
                        "Excellent value for the features",  # Positive feedback, balances cost and capabilities
                        "Overpriced for what it offers",  # Negative feedback, criticizes the price relative to features
                        "Very satisfied with this purchase",  # Strong positive feedback on the overall experience
                        "Extremely dissatisfied",  # Strong negative feedback on the overall experience
                        "Would definitely purchase again in the future",  # Positive indication of future engagement
                        "Will not be buying from this seller again",  # Negative indication of future engagement
                        "The packaging was excellent", # Positive feedback on presentation
                        "The packaging was damaged", # Negative feedback on presentation
                        "Arrived much sooner than expected", # Very positive feedback on delivery speed
                        "Delivery took much longer than stated", # Negative feedback on delivery time
                        "The instructions were clear and easy to follow", # Positive feedback on usability documentation
                        "The instructions were confusing and unhelpful", # Negative feedback on usability documentation
                    ]
                    commentContent = random.choice(comments)
                    
                    try:
                        await addComment(
                            self.dbSession,
                            review_id=reviewId,
                            user_id=userId,
                            content=commentContent
                        )
                    except SQLAlchemyError as e:
                        raise CommentGenerationError(f"Failed to generate comment: {str(e)}") from e
        except SQLAlchemyError as e:
            raise ReviewGenerationError(f"Failed to generate reviews and comments: {str(e)}") from e

    @logMethod
    async def generateAllData(self):
        """
        Generates all test data in a single transaction.
        If any step fails, all changes are rolled back.
        Steps:
        1. Check if dummy data already exists
        2. Insert locations
        3. Insert users
        4. Insert orders
        5. Insert order-item associations
        6. Insert reviews and comments
        7. Add dummy data flag
        
        Raises:
            DataGeneratorException: If any step fails, with details about which step failed
        """
        existingData = await getMetaData(self.dbSession, "dummyData")
        if existingData:
            return
        try:
            await self.insertDummyLocations()
            await self.insertFakeUsers()
            await self.insertFakeOrders()
            await self.insertFakeOrderItemAssociation()
            await self.insertFakeReviewsAndComments()
            await addMetaData(self.dbSession, "dummyData", "true")
        except DataGeneratorException as e:
            raise DataGeneratorException(f"Data generation failed: {str(e)}") from e
        except SQLAlchemyError as e:
            raise DataGeneratorException(f"Database error during data generation: {str(e)}") from e


            



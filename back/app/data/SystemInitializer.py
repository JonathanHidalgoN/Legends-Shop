from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.data.ItemsLoader import ItemsLoader
from app.data.DataGenerator import DataGenerator
from app.delivery.DeliveryDateAssigner import DeliveryDateAssigner
from app.data.utils import getAllItemTableRowsAnMapToItems
from app.customExceptions import SameVersionUpdateError, SystemInitializationError
from app.logger import logMethod, logger
from app.schemas.Item import Item


class SystemInitializer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.itemsLoader: ItemsLoader | None = None
        self.dataGenerator: DataGenerator | None = None
        self.deliveryAssigner: DeliveryDateAssigner | None = None
        self.items: List[Item] = []

    @logMethod
    async def initializeItemLoader(self) -> None:
        """Initialize and update items from external source"""
        try:
            self.itemsLoader = ItemsLoader(self.db)
            try:
                await self.itemsLoader.updateItems()
            except SameVersionUpdateError:
                logger.info("Items are already at the latest version")
        except Exception as e:
            raise SystemInitializationError(f"Failed to initialize ItemsLoader: {str(e)}")

    @logMethod
    async def loadItems(self) -> None:
        """Load items from database"""
        try:
            self.items = await getAllItemTableRowsAnMapToItems(self.db)
            if not self.items:
                raise SystemInitializationError("No items found in database")
        except Exception as e:
            raise SystemInitializationError(f"Failed to load items: {str(e)}")

    @logMethod
    async def initializeDataGenerator(self) -> None:
        """Initialize data generator and create basic data"""
        try:
            self.dataGenerator = DataGenerator(self.db, self.items)
            await self.dataGenerator.insertDummyLocations()
            await self.dataGenerator.insertFakeUsers()
        except Exception as e:
            raise SystemInitializationError(f"Failed to initialize basic data: {str(e)}")

    @logMethod
    async def initializeDeliveryDates(self) -> None:
        """Initialize delivery date system"""
        try:
            self.deliveryAssigner = DeliveryDateAssigner(self.db)
            await self.deliveryAssigner.checkAndUpdateDeliveryDates()
        except Exception as e:
            raise SystemInitializationError(f"Failed to initialize delivery dates: {str(e)}")

    @logMethod
    async def generateOrdersAndReviews(self) -> None:
        """Generate orders and reviews after all prerequisites are met"""
        try:
            if not self.dataGenerator:
                raise SystemInitializationError("Data generator not initialized")
            await self.dataGenerator.insertFakeOrders(self.dataGenerator.userIds, self.dataGenerator.locationIds)
            await self.dataGenerator.insertFakeOrderItemAssociation(self.dataGenerator.orderIds, self.dataGenerator.itemIds)
            await self.dataGenerator.insertFakeReviewsAndComments(self.dataGenerator.orderIds, self.dataGenerator.userIds)
        except Exception as e:
            raise SystemInitializationError(f"Failed to generate orders and reviews: {str(e)}")

    @logMethod
    async def initializeSystem(self) -> None:
        """
        Main initialization method that orchestrates the entire system initialization
        in the correct order:
        1. Initialize items loader and update items
        2. Load items from database
        3. Initialize data generator and create locations and users
        4. Initialize delivery dates
        5. Generate orders and reviews
        """
        try:
            await self.initializeItemLoader()
            await self.loadItems()
            await self.initializeDataGenerator()
            await self.initializeDeliveryDates()
            await self.generateOrdersAndReviews()
        except SystemInitializationError as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during system initialization: {str(e)}")
            raise SystemInitializationError(f"System initialization failed: {str(e)}") 

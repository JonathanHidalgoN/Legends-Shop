from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.data.ItemsLoader import ItemsLoader
from app.data.DataGenerator import DataGenerator
from app.delivery.DeliveryDateAssigner import DeliveryDateAssigner
from app.data.utils import getAllItemTableRowsAnMapToItems
from app.customExceptions import SystemInitializationError
from app.logger import logMethod, logger
from app.schemas.Item import Item
from app.data.queries.metaDataQueries import getMetaData, addMetaData


class SystemInitializer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.itemsLoader: ItemsLoader | None = None
        self.dataGenerator: DataGenerator | None = None
        self.deliveryAssigner: DeliveryDateAssigner | None = None
        self.items: List[Item] = []
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @logMethod
    async def checkInitializationStatus(self) -> bool:
        """Check if system has been previously initialized"""
        try:
            status = await getMetaData(self.db, "system_initialized")
            return status == "true"
        except Exception:
            return False

    @logMethod
    async def markInitializationComplete(self) -> None:
        """Mark system as initialized"""
        try:
            await addMetaData(self.db, "system_initialized", "true")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to mark system as initialized: {str(e)}")
            raise SystemInitializationError("Failed to mark system as initialized")

    @logMethod
    async def initializeItemLoader(self) -> None:
        """Initialize and update items from external source"""
        try:
            logger.info("Starting ItemsLoader initialization...")
            self.itemsLoader = ItemsLoader(self.db)
            await self.itemsLoader.updateItems()
            logger.info("ItemsLoader initialization completed")
        except Exception as e:
            logger.error(f"ItemsLoader initialization failed: {str(e)}")
            raise SystemInitializationError(f"Failed to initialize ItemsLoader: {str(e)}")

    @logMethod
    async def loadItems(self) -> None:
        """Load items from database"""
        try:
            logger.info("Loading items from database...")
            self.items = await getAllItemTableRowsAnMapToItems(self.db)
            if not self.items:
                logger.error("No items found in database")
                raise SystemInitializationError("No items found in database")
            logger.info(f"Successfully loaded {len(self.items)} items")
        except Exception as e:
            logger.error(f"Failed to load items: {str(e)}")
            raise SystemInitializationError(f"Failed to load items: {str(e)}")

    @logMethod
    async def initializeDataGenerator(self) -> None:
        """Initialize data generator and create basic data"""
        try:
            logger.info("Initializing data generator...")
            self.dataGenerator = DataGenerator(self.db, self.items)
            # First create locations as they are needed for delivery dates
            logger.info("Inserting locations...")
            await self.dataGenerator.insertDummyLocations()
            # Then create users as they are independent
            logger.info("Inserting users...")
            await self.dataGenerator.insertFakeUsers()
            logger.info("Data generator initialization completed")
        except Exception as e:
            logger.error(f"Data generator initialization failed: {str(e)}")
            raise SystemInitializationError(f"Failed to initialize basic data: {str(e)}")

    @logMethod
    async def initializeDeliveryDates(self) -> None:
        """Initialize delivery date system"""
        try:
            logger.info("Initializing delivery dates...")
            self.deliveryAssigner = DeliveryDateAssigner(self.db)
            await self.deliveryAssigner.checkAndUpdateDeliveryDates()
            logger.info("Delivery dates initialization completed")
        except Exception as e:
            logger.error(f"Delivery dates initialization failed: {str(e)}")
            raise SystemInitializationError(f"Failed to initialize delivery dates: {str(e)}")

    @logMethod
    async def generateOrdersAndReviews(self) -> None:
        """Generate orders and reviews after all prerequisites are met"""
        try:
            logger.info("Generating orders and reviews...")
            if not self.dataGenerator:
                raise SystemInitializationError("Data generator not initialized")
            
            # Now we can create orders since we have locations, users and delivery dates
            logger.info("Inserting orders...")
            await self.dataGenerator.insertFakeOrders(
                self.dataGenerator.userIds, 
                self.dataGenerator.locationIds
            )
            
            # Then create order-item associations
            logger.info("Creating order-item associations...")
            await self.dataGenerator.insertFakeOrderItemAssociation(
                self.dataGenerator.orderIds, 
                self.dataGenerator.itemIds
            )
            
            # Finally create reviews and comments
            logger.info("Generating reviews and comments...")
            await self.dataGenerator.insertFakeReviewsAndComments(
                self.dataGenerator.orderIds, 
                self.dataGenerator.userIds
            )
            logger.info("Orders and reviews generation completed")
        except Exception as e:
            logger.error(f"Orders and reviews generation failed: {str(e)}")
            raise SystemInitializationError(f"Failed to generate orders and reviews: {str(e)}")

    @logMethod
    async def initializeSystem(self) -> None:
        """
        Main initialization method that orchestrates the entire system initialization
        in the correct order:
        1. Check if system was previously initialized
        2. Initialize items loader and update items
        3. Load items from database
        4. Initialize data generator and create locations and users
        5. Initialize delivery dates
        6. Generate orders and reviews
        7. Mark initialization as complete
        """
        try:
            # Check if system was already initialized
            if await self.checkInitializationStatus():
                logger.info("System was previously initialized, loading existing data...")
                await self.loadItems()
                self._initialized = True
                return

            logger.info("Starting full system initialization...")
            
            # Start initialization process
            await self.initializeItemLoader()
            await self.loadItems()
            await self.initializeDataGenerator()
            await self.initializeDeliveryDates()
            await self.generateOrdersAndReviews()
            
            # Mark initialization as complete
            await self.markInitializationComplete()
            await self.db.commit()
            logger.info("System initialization completed successfully")
            
        except SystemInitializationError as e:
            logger.error(f"System initialization failed: {str(e)}")
            await self.db.rollback()  # Ensure we rollback any pending changes
            raise
        except Exception as e:
            logger.error(f"Unexpected error during system initialization: {str(e)}")
            await self.db.rollback()  # Ensure we rollback any pending changes
            raise SystemInitializationError(f"System initialization failed: {str(e)}") 

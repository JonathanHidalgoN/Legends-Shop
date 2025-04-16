from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.data.database import AsyncSessionLocal
from app.services.OrderStatusProcessor import OrderStatusProcessor
from app.data.ItemsLoader import ItemsLoader
from app.delivery.DeliveryDateAssigner import DeliveryDateAssigner
from app.logger import logger


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.itemsLoader = None

        """Initialize the ItemsLoader with a database session"""

    async def initializeItemsLoader(self, db):
        self.itemsLoader = ItemsLoader(db)

    async def updateOrderStatusJob(self):
        async with AsyncSessionLocal() as db:
            processor = OrderStatusProcessor(db)
            await processor.updateOrderStatuses()

    async def updateItemsJob(self):
        async with AsyncSessionLocal() as db:
            try:
                if not self.itemsLoader:
                    await self.initializeItemsLoader(db)
                if self.itemsLoader:
                    await self.itemsLoader.updateItems()
                else:
                    logger.error("ItemsLoader not initialized")
            except Exception as e:
                logger.error(f"Error updating items: {str(e)}")

    async def assignDeliveryDatesJob(self):
        async with AsyncSessionLocal() as db:
            try:
                assigner = DeliveryDateAssigner(db)
                await assigner.checkAndUpdateDeliveryDates()
                logger.info("Delivery dates assigned successfully")
            except Exception as e:
                logger.error(f"Error assigning delivery dates: {str(e)}")

    def start(self):
        # Schedule jobs to run every day at slightly different times
        self.scheduler.add_job(
            self.updateOrderStatusJob,
            trigger=CronTrigger(hour=0, minute=0),  # 00:00
            id="update_order_statuses",
            name="Update order statuses",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.updateItemsJob,
            trigger=CronTrigger(hour=0, minute=5),  # 00:05
            id="update_items",
            name="Update items from API",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.assignDeliveryDatesJob,
            trigger=CronTrigger(hour=0, minute=15),  # 00:15
            id="assign_delivery_dates",
            name="Assign delivery dates",
            replace_existing=True,
        )

        self.scheduler.start()

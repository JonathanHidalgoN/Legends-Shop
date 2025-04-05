from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.data.database import AsyncSessionLocal
from app.services.OrderStatusProcessor import OrderStatusProcessor
from app.data.ItemsLoader import ItemsLoader
from app.customExceptions import SameVersionUpdateError
from app.logger import logger


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def updateOrderStatusJob(self):
        async with AsyncSessionLocal() as db:
            processor = OrderStatusProcessor(db)
            await processor.update_order_statuses()

    async def updateItemsJob(self):
        async with AsyncSessionLocal() as db:
            try:
                itemsLoader = ItemsLoader(db)
                await itemsLoader.updateItems()
            except SameVersionUpdateError:
                # This is expected when the version hasn't changed
                logger.info("Items are already up to date")
            except Exception as e:
                # Log the error but don't raise it to prevent the scheduler from stopping
                logger.error(f"Error updating items: {str(e)}")

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

        self.scheduler.start()

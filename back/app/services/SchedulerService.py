from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.data.database import AsyncSessionLocal
from app.services.OrderStatusProcessor import OrderStatusProcessor


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def updateOrderStatusJob(self):
        async with AsyncSessionLocal() as db:
            processor = OrderStatusProcessor(db)
            await processor.update_order_statuses()

    def start(self):
        # Schedule job to run every day at 12:00 PM
        self.scheduler.add_job(
            self.updateOrderStatusJob,
            trigger=CronTrigger(hour=12, minute=0),
            id="update_order_statuses",
            name="Update order statuses",
            replace_existing=True,
        )
        self.scheduler.start()

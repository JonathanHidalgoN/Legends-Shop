import random
from typing import Sequence
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.data.models.DeliveryDatesTable import ItemLocationDeliveryAssociation
from app.customExceptions import (
    DeliveryDateAssignerException,
    LocationNotFoundException,
    ItemNotFoundException,
)
from app.auth.functions import logMethod
from app.data.queries.itemQueries import getAllItemIds
from app.data.queries.locationQueries import getAllLocationIds
from datetime import datetime, timedelta
from app.schemas.DeliveryDate import DeliveryDate


class DeliveryDateAssigner:
    def __init__(self, asyncSession: AsyncSession):
        self.dbSession = asyncSession

    def createRandomDays(self) -> int:
        """Create a random number of days between 1 and 14."""
        return random.randint(1, 14)

    @logMethod
    async def getDeliveryDates(self, itemIds: list[int], locationId: int) -> list[DeliveryDate]:
        """Get delivery dates for a list of items based on location."""
        try:
            # Query the delivery dates for the given items and location
            query = select(ItemLocationDeliveryAssociation).where(
                ItemLocationDeliveryAssociation.item_id.in_(itemIds),
                ItemLocationDeliveryAssociation.location_id == locationId
            )
            result = await self.dbSession.execute(query)
            associations = result.scalars().all()

            # Calculate delivery dates based on days_plus
            today = datetime.now().date()
            delivery_dates = []
            for association in associations:
                delivery_date = today + timedelta(days=association.days_plus)
                delivery_dates.append(DeliveryDate(
                    itemId=association.item_id,
                    locationId=association.location_id,
                    deliveryDate=delivery_date
                ))

            return delivery_dates

        except Exception as e:
            raise DeliveryDateAssignerException(f"Failed to get delivery dates: {str(e)}")

    @logMethod
    async def assignDeliveryDates(self) -> None:
        """Assign random delivery days to each item for each location."""
        try:
            # Get all locations and items using the new query functions
            locationIds: Sequence[int] = await getAllLocationIds(self.dbSession)
            itemIds = await getAllItemIds(self.dbSession)

            if not locationIds:
                raise LocationNotFoundException("No locations found in the database")
            if not itemIds:
                raise ItemNotFoundException("No items found in the database")

            # Create delivery date assignments
            for locationId in locationIds:
                for itemId in itemIds:
                    daysPlus = self.createRandomDays()
                    association = {
                        "item_id": itemId,
                        "location_id": locationId,
                        "days_plus": daysPlus
                    }
                    ins = insert(ItemLocationDeliveryAssociation).values(**association)
                    await self.dbSession.execute(ins)

            await self.dbSession.commit()

        except Exception as e:
            await self.dbSession.rollback()
            raise DeliveryDateAssignerException(f"Failed to assign delivery days: {str(e)}") 
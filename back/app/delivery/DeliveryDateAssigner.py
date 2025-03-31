import random
from typing import Sequence
from sqlalchemy import insert
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


class DeliveryDateAssigner:
    def __init__(self, asyncSession: AsyncSession):
        self.dbSession = asyncSession

    def createRandomDays(self) -> int:
        """Create a random number of days between 1 and 14."""
        return random.randint(1, 14)

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
                                "item_id":itemId,
                        "location_id":locationId,
                        "days_plus":daysPlus
                    }
                    ins = insert(ItemLocationDeliveryAssociation).values(**association)
                    await self.dbSession.execute(ins)

            await self.dbSession.commit()

        except Exception as e:
            await self.dbSession.rollback()
            raise DeliveryDateAssignerException(f"Failed to assign delivery days: {str(e)}") 

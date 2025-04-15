import random
from typing import List, Sequence
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.data.models.DeliveryDatesTable import ItemLocationDeliveryAssociation
from app.customExceptions import (
    DeliveryDateAssignerException,
    LocationNotFoundException,
    ItemNotFoundException,
)
from app.logger import logMethod, logger
from app.data.queries.itemQueries import getAllItemIds
from app.data.queries.locationQueries import getAllLocationIds
from app.data.queries.metaDataQueries import getMetaData, addMetaData
from app.schemas.DeliveryDate import DeliveryDate
from app.data.queries.deliveryDatesQueries import getAllDeliveryDatesByLocationId
from sqlalchemy.dialects.postgresql import insert as pg_insert


class DeliveryDateAssigner:
    def __init__(self, asyncSession: AsyncSession):
        self.dbSession = asyncSession

    def createRandomDays(self) -> int:
        """Create a random number of days between 1 and 14."""
        return random.randint(1, 14)

    @logMethod
    async def getItemDeliveryDates(self, locationId: int) -> List[DeliveryDate]:
        """Get delivery dates for a list of items based on location."""
        try:
            deliveryDates: List[DeliveryDate] = await getAllDeliveryDatesByLocationId(
                self.dbSession, locationId
            )
            return deliveryDates

        except Exception as e:
            raise DeliveryDateAssignerException(
                f"Failed to get delivery dates: {str(e)}"
            )

    @logMethod
    async def checkAndUpdateDeliveryDates(self) -> None:
        """
        Check if delivery dates need to be updated based on metadata.
        If the last update date is not today, update the delivery dates.
        """
        try:
            lastUpdateStr = await getMetaData(self.dbSession, "delivery_date_updated")

            if not lastUpdateStr or date.fromisoformat(lastUpdateStr) != date.today():
                await self.assignDeliveryDates()

                await addMetaData(
                    self.dbSession, "delivery_date_updated", date.today().isoformat()
                )
                logger.info("Delivery dates updated and metadata recorded")
            else:
                logger.info("Delivery dates are already up to date")

        except Exception as e:
            raise DeliveryDateAssignerException(
                f"Failed to check and update delivery dates: {str(e)}"
            ) from e

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
                        "days_plus": daysPlus,
                    }
                    ins = pg_insert(ItemLocationDeliveryAssociation).values(
                        **association
                    )
                    ins = ins.on_conflict_do_update(
                        constraint="item_location_delivery_association_pkey",
                        set_=dict(days_plus=daysPlus),
                    )
                    await self.dbSession.execute(ins)

            await self.dbSession.commit()

        except Exception as e:
            await self.dbSession.rollback()
            raise DeliveryDateAssignerException(
                f"Failed to assign delivery days: {str(e)}"
            )

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.data.models.DeliveryDatesTable import ItemLocationDeliveryAssociation
from typing import List

from datetime import date, timedelta
from typing import List

from app.schemas.DeliveryDate import DeliveryDate


async def getAllDeliveryDatesByLocationId(
    asyncSession: AsyncSession, locationId: int
) -> List[DeliveryDate]:
    """
    Get all delivery dates for a specific location.
    
    Args:
        asyncSession: The database session.
        locationId: The ID of the location to get delivery dates for.
        
    Returns:
        A list of DeliveryDate objects containing itemId, locationId, and the computed deliveryDate.
    """
    query = select(ItemLocationDeliveryAssociation).where(
        ItemLocationDeliveryAssociation.c.location_id == locationId
    )
    result = await asyncSession.execute(query)
    rows = result.fetchall()  # Get all matching rows

    delivery_dates = [
        DeliveryDate(
            itemId=row.item_id,
            locationId=row.location_id,
            deliveryDate=date.today() + timedelta(days=row.days_plus)
        )
        for row in rows
    ]
    return delivery_dates

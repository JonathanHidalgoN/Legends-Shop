from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.CartTable import CartTable
from app.schemas.Order import CartStatus

async def getAddedCartItemsWithUserId(
    asyncSession: AsyncSession, userId: int
) -> List[CartTable]:
    """ """
    result = await asyncSession.execute(
        select(CartTable).where((CartTable.user_id == userId) & 
            (CartTable.status == CartStatus.ADDED)
        ))
    cartTableRows : List[CartTable] = [row for row in result.scalars().all()]
    return cartTableRows 

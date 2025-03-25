from typing import List
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.CartTable import CartTable
from app.schemas.Order import CartStatus


async def getAddedCartItemsWithUserId(
    asyncSession: AsyncSession, userId: int
) -> List[CartTable]:
    """ """
    result = await asyncSession.execute(
        select(CartTable).where(
            (CartTable.user_id == userId) & (CartTable.status == CartStatus.ADDED)
        )
    )
    cartTableRows: List[CartTable] = [row for row in result.scalars().all()]
    return cartTableRows


async def changeCartItemStatusToDeleted(
    asyncSession: AsyncSession, userId: int, cartRowId: int
) -> None:
    await asyncSession.execute(
        update(CartTable)
        .where(
            (CartTable.id == cartRowId)
            & (CartTable.user_id == userId)
            & (CartTable.status == CartStatus.ADDED)
        )
        .values(status=CartStatus.DELETED)
    )
    await asyncSession.commit()

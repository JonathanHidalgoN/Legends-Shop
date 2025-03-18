from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable


async def getCurrentUserGoldWithUserName(
    asyncSession: AsyncSession, userName: str
) -> int | None:
    """ """
    result = await asyncSession.execute(
        select(UserTable.current_gold).where(UserTable.userName == userName)
    )
    userGold: int | None = result.scalars().first()
    return userGold


async def getCurrentUserGoldWithUserId(
    asyncSession: AsyncSession, userId: int
) -> int | None:
    """ """
    result = await asyncSession.execute(
        select(UserTable.current_gold).where(UserTable.id == userId)
    )
    userGold: int | None = result.scalars().first()
    return userGold

async def getTotalSpendUserGoldWithUserId(
    asyncSession: AsyncSession, userId: int
) -> int | None:
    """ """
    result = await asyncSession.execute(
        select(UserTable.gold_spend).where(UserTable.id == userId)
    )
    userSpendGold: int | None = result.scalars().first()
    return userSpendGold

async def updateUserGoldWithUserId(
    asyncSession: AsyncSession, userId: int, newGold: int
) -> None:
    """ """
    result = await asyncSession.execute(
        update(UserTable).where(UserTable.id == userId).values(current_gold=newGold)
    )
    if result.rowcount == 0:
        raise SQLAlchemyError(
            f"Tried to update current_gold row of table UserTable with user id {userId} but 0 rows where updated"
        )
    await asyncSession.commit()

async def updateUserSpendGoldWithUserId(
    asyncSession: AsyncSession, userId: int, newGold: int
) -> None:
    """ """
    result = await asyncSession.execute(
        update(UserTable).where(UserTable.id == userId).values(gold_spend=newGold)
    )
    if result.rowcount == 0:
        raise SQLAlchemyError(
            f"Tried to update spend_gold row of table UserTable with user id {userId} but 0 rows where updated"
        )
    await asyncSession.commit()

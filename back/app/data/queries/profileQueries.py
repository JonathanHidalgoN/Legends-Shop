from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable


async def getCurrentUserGoldWithUserName(asyncSession: AsyncSession, userName: str) -> int | None:
    """
    """
    result = await asyncSession.execute(
        select(UserTable.current_gold).where(UserTable.userName == userName)
    )
    userGold: int | None = result.scalars().first()
    return userGold 


async def getCurrentUserGoldWithUserId(asyncSession: AsyncSession, userId: int) -> int | None:
    """
    """
    result = await asyncSession.execute(
        select(UserTable.current_gold).where(UserTable.id == userId)
    )
    userGold: int | None = result.scalars().first()
    return userGold 

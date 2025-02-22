from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable
from app.schemas.AuthSchemas import UserInDB

async def getUserInDB(asyncSession: AsyncSession, userName: str) -> UserInDB | None:
    """
    Retrieve the user from the database if they exist.
    """
    result = await asyncSession.execute(
        select(UserTable.userName, UserTable.password).where(UserTable.userName == userName)
    )
    row = result.first()  
    if row is None:
        return None
    username, hashed_password = row
    return UserInDB(userName=username, hashedPassword=hashed_password)

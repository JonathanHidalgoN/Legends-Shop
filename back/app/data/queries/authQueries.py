from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.mappers import mapUserInDBToUserTable
from app.data.models.UserTable import UserTable
from app.schemas.AuthSchemas import UserInDB


async def getUserInDB(asyncSession: AsyncSession, userName: str) -> UserInDB | None:
    """
    Retrieve the user from the database if they exist.
    """
    result = await asyncSession.execute(
        select(UserTable.userName, UserTable.password).where(
            UserTable.userName == userName
        )
    )
    row = result.first()
    if row is None:
        return None
    username, hashed_password = row
    return UserInDB(userName=username, hashedPassword=hashed_password)


async def checkUserExistInDB(asyncSession: AsyncSession, userName: str) -> bool:
    """
    Check if a user exist in db
    """
    result = await asyncSession.execute(
        select(UserTable.userName).where(UserTable.userName == userName)
    )
    row = result.first()
    if row is None:
        return False
    return True


async def insertUser(asyncSession: AsyncSession, userInDB: UserInDB) -> None:
    """
    Insert a new user into the database.
    """
    userTable: UserTable = mapUserInDBToUserTable(userInDB)

    asyncSession.add(userTable)
    await asyncSession.commit()
    await asyncSession.refresh(userTable)


async def getUserIdWithUserName(
    asyncSession: AsyncSession, userName: str
) -> int | None:
    """
    Get the user id with userName.
    """
    result = await asyncSession.execute(
        select(UserTable.id).where(UserTable.userName == userName)
    )
    userId = result.scalars().first()
    return userId

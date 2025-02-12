from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# This function gets the databaseUrl
def getDatabaseUrl() -> str:
    load_dotenv()
    databaseUrl = os.getenv("DATABASE_URL", "Empty")
    return databaseUrl


load_dotenv()
DATABASE_URL: str = getDatabaseUrl()
# Modules are singletons, first import will create this object and the subsequent imports
# will use the same instance
# Docs: https://docs.sqlalchemy.org/en/20/tutorial/engine.html#tutorial-engine
engine = create_async_engine(DATABASE_URL, echo=True)
base = declarative_base()
AsyncSessionLocal = async_sessionmaker(engine, autoflush=False)


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-httpexception
# With yield can execute cleanup
async def getDbSession() -> AsyncGenerator[AsyncSession, None]:
    # Change from asyncSession to asyncSessionLocal to bind it to the engine
    async with AsyncSessionLocal() as session:
        yield session

import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# This is run with docker, so the compose has to inject the environmet variables
# This won't run local, because in this dir is not the .env file
# TODO: add code to run locally
load_dotenv()
DATABASE_URL = os.getenv("INTERNAL_DATABASE_URL", "Empty")


# Modules are singletons, first import will create this object and the subsequent imports
# will use the same instance
# Docs: https://docs.sqlalchemy.org/en/20/tutorial/engine.html#tutorial-engine
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, autoflush=False)


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-httpexception
# With yield can execute cleanup
async def getDbSession() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession() as session:
        yield session

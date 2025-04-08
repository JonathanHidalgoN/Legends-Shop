from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.envVariables import DATABASE_URL


# Modules are singletons, first import will create this object and the subsequent imports
# will use the same instance
# Docs: https://docs.sqlalchemy.org/en/20/tutorial/engine.html#tutorial-engine
engine = create_async_engine(DATABASE_URL, echo=True)
#All tables have to be an instance of this to be managed together
base = declarative_base()
AsyncSessionLocal = async_sessionmaker(engine, autoflush=False)


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-httpexception
# With yield can execute cleanup
async def getDbSession() -> AsyncGenerator[AsyncSession, None]:
    # Change from asyncSession to asyncSessionLocal to bind it to the engine
    async with AsyncSessionLocal() as session:
        yield session

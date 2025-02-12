from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.data.ItemsLoader import ItemsLoader
from app.routes import items

app = FastAPI()
app.include_router(items.router, prefix="/items")


@app.get("/")
async def root(db: AsyncSession = Depends(database.getDbSession)):
    return {"message": database.getDatabaseUrl()}


@app.get("/testUpdateTagsTable")
async def testUpdateTagsTable(db: AsyncSession = Depends(database.getDbSession)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    await itemsLoader.updateItems()
    return {"message": "tested"}


@app.get("/testGetVersion")
async def testUpdateVersion(db: AsyncSession = Depends(database.getDbSession)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    version = await itemsLoader.getLastVersion()
    return {"message": version}

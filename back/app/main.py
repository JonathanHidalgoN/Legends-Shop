from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.data.ItemsLoaderDemo import ItemsLoader
from app.data.utils import getDatabaseUrl

app = FastAPI()

# to run normally :uvicorn app.main:app
# to attach debbuger :python -m debugpy --listen 5679 --wait-for-client -m uvicorn app.main:app --host 127.0.0.1 --port 8000


@app.get("/")
async def root(db: AsyncSession = Depends(database.getDbSession)):
    return {"message": getDatabaseUrl()}


@app.get("/testUpdateTagsTable")
async def testUpdateTagsTable(db: AsyncSession = Depends(database.getDbSession)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    await itemsLoader.updateItems()
    return {"message": "tested"}

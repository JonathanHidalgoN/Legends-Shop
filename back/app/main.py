from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.data.ItemsLoader import ItemsLoader
from app.data.queries.itemQueries import getVersion
from app.routes import items, auth
from fastapi.middleware.cors import CORSMiddleware
from app.envVariables import FRONTEND_HOST, FRONTEND_PORT

app = FastAPI()
app.include_router(items.router, prefix="/items")
app.include_router(auth.router, prefix="/auth")

origins = [f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(db: AsyncSession = Depends(database.getDbSession)):
    version: str | None = await getVersion(db)
    return {"message": version}


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

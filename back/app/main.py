from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.data.ItemsLoader import ItemsLoader
from app.data.queries.itemQueries import getVersion
from app.routes import items, auth, orders
from fastapi.middleware.cors import CORSMiddleware
from app.envVariables import FRONTEND_HOST, FRONTEND_PORT

app = FastAPI()
origins = [
    f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"
    # TODO: add env variable to website that host the frontend client
    ,
    f"http://localhost:{FRONTEND_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/items")
app.include_router(auth.router, prefix="/auth")
app.include_router(orders.router, prefix="/orders")


@app.get("/")
async def root():
    return {"message": "up"}

@app.get("/db")
async def db_status(db: AsyncSession = Depends(database.getDbSession)):
    try:
        await db.execute(text("SELECT 1"))
        return {"message": "Database is connected and healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

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

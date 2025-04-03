from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from httpx import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.data.ItemsLoader import ItemsLoader
from app.routes import items, auth, orders, profile, cart, deliveryDates, locations
from fastapi.middleware.cors import CORSMiddleware
from app.envVariables import FRONTEND_HOST, FRONTEND_PORT
from app.logger import logger
from app.customExceptions import ItemsLoaderError, SameVersionUpdateError
from app.services.SchedulerService import SchedulerService
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = SchedulerService()
    scheduler.start()
    yield
    scheduler.scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(
        f"Response status: {response.status_code} for {request.method} {request.url}"
    )
    return response


origins = [
    FRONTEND_HOST
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
app.include_router(profile.router, prefix="/profile")
app.include_router(cart.router, prefix="/cart")
app.include_router(deliveryDates.router, prefix="/delivery_dates")
app.include_router(locations.router, prefix="/locations")


def getItemsLoader(
    db: AsyncSession = Depends(database.getDbSession),
) -> ItemsLoader:
    return ItemsLoader(db)


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
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


@app.get("/testUpdateTagsTable")
async def testUpdateTagsTable(db: AsyncSession = Depends(database.getDbSession)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    await itemsLoader.updateItemsStepsJob()
    return {"message": "tested"}


@app.get("/testGetVersion")
async def testUpdateVersion(db: AsyncSession = Depends(database.getDbSession)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    version = await itemsLoader.getLastVersion()
    return {"message": version}


@app.put("/updateItems", include_in_schema=False)
async def updateItems(itemsLoader: Annotated[ItemsLoader, Depends(getItemsLoader)]):
    try:
        await itemsLoader.updateItems()
    except SameVersionUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ItemsLoaderError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")

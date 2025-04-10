from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from app.data import database
from app.data.ItemsLoader import ItemsLoader
from app.routes import items, auth, orders, profile, cart, deliveryDates, locations
from fastapi.middleware.cors import CORSMiddleware
from app.envVariables import FRONTEND_HOST, FRONTEND_PORT
from app.customExceptions import ItemsLoaderError, SameVersionUpdateError
from app.services.SchedulerService import SchedulerService
from contextlib import asynccontextmanager
from app.rateLimiter import limiter
from app.routes import reviews
from app.routes.RequestLoggingMiddleware import RequestLoggingMiddleware
from app.routes.SecurityHeadersMiddleware import SecurityHeadersMiddleware
from app.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = SchedulerService()
    scheduler.start()
    yield
    scheduler.scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

@app.exception_handler(429)
async def tooManyRequestHanlder():
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


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
app.include_router(reviews.router, prefix="/review")
app.include_router(health.router, prefix="/health")


def getItemsLoader(
    db: AsyncSession = Depends(database.getDbSession),
) -> ItemsLoader:
    return ItemsLoader(db)




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

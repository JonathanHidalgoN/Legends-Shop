from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from app.data.database import AsyncSessionLocal
from app.data.ItemsLoader import ItemsLoader
from app.data.SystemInitializer import SystemInitializer
from app.services.SchedulerService import SchedulerService
from contextlib import asynccontextmanager
from app.rateLimiter import limiter
from app.routes import reviews, items, auth, orders, profile, cart, deliveryDates, locations
from app.routes.RequestLoggingMiddleware import RequestLoggingMiddleware
from app.routes.SecurityHeadersMiddleware import SecurityHeadersMiddleware
from app.routes import health
from app.logger import logger
from app.customExceptions import SystemInitializationError
from fastapi.middleware.cors import CORSMiddleware
from app.envVariables import FRONTEND_HOST, FRONTEND_PORT, USE_PROMETHEUS

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = SchedulerService()

    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting system initialization...")
            systemInitializer = SystemInitializer(db)
            await systemInitializer.initializeSystem()
            logger.info("System initialization completed successfully")
            scheduler.itemsLoader = systemInitializer.itemsLoader
        except SystemInitializationError as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during startup: {str(e)}")
            raise

    scheduler.start()
    yield
    scheduler.scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter


@app.exception_handler(429)
async def tooManyRequestHanlder(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"},
    )

#This will mess with fastapi configs, find another way of using prometeus with python 
# if USE_PROMETHEUS:
#     from fastapi_prometheus_exporter import PrometheusExporterMiddleware
#     PrometheusExporterMiddleware.setup(
#         app=app,
#         metrics_path="/metrics",
#         ignore_paths=["/health", "/metrics"],
#     )

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


@app.get("/testGetVersion")
async def testUpdateVersion(db: AsyncSession = Depends(AsyncSessionLocal)):
    itemsLoader: ItemsLoader = ItemsLoader(db)
    version = await itemsLoader.getLastVersion()
    return {"message": version}

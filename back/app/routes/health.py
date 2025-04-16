from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.data import database
from app.logger import logger
from app.data.ItemsLoader import ItemsLoader
from typing import Dict, Any
from app.rateLimiter import apiRateLimit

router = APIRouter()


@router.get("/", summary="Basic health check")
@apiRateLimit()
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint that returns a simple status message.
    This endpoint is lightweight and can be used for basic availability checks.
    """
    return {"status": "healthy"}


@router.get("/health/detailed", summary="Detailed health check")
async def detailed_health_check(
    db: AsyncSession = Depends(database.getDbSession),
) -> Dict[str, Any]:
    """
    Detailed health check that verifies database connectivity and other critical services.
    This endpoint provides more comprehensive health information.
    """
    health_status = {
        "status": "healthy",
        "services": {"database": "healthy", "items_loader": "healthy"},
    }

    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "degraded"
        health_status["services"]["database"] = "unhealthy"

    # Check items loader service
    try:
        items_loader = ItemsLoader(db)
        await items_loader.getLastVersion()
    except Exception as e:
        logger.error(f"Items loader health check failed: {str(e)}")
        health_status["status"] = "degraded"
        health_status["services"]["items_loader"] = "unhealthy"

    return health_status


@router.get("/health/readiness", summary="Readiness probe")
async def readiness_probe() -> Dict[str, str]:
    """
    This endpoint indicates whether the application is ready to receive traffic.
    """
    return {"status": "ready"}


@router.get("/health/liveness", summary="Liveness probe")
@apiRateLimit()
async def liveness_probe() -> Dict[str, str]:
    """
    This endpoint indicates whether the application is alive and functioning.
    """
    return {"status": "alive"}

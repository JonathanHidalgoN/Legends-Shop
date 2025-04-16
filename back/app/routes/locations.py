from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.location.LocationManager import LocationManager
from app.customExceptions import (
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.data import database
from app.schemas.Location import Location
from app.routes.auth import getUserIdFromName
from app.data.mappers import mapLocationTableToLocation
from app.data.queries.locationQueries import getUserLocation
from app.logger import logger
from app.rateLimiter import apiRateLimit, sensitiveRateLimit

router = APIRouter()


async def getLocationManager(
    dbSession: Annotated[AsyncSession, Depends(database.getDbSession)],
) -> LocationManager:
    return LocationManager(dbSession)


@router.get("/all")
@apiRateLimit()
async def getAllLocations(
    locationManager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Get all locations.
    """
    try:
        return await locationManager.getAllLocations()
    except LocationManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user", response_model=Location)
@apiRateLimit()
async def getUserLocationEndpoint(
    userId: Annotated[int | None, Depends(getUserIdFromName)],
    dbSession: Annotated[AsyncSession, Depends(database.getDbSession)],
):
    """
    Get the location for the current user.
    """
    if userId is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        location = await getUserLocation(dbSession, userId)
        if location is None:
            raise HTTPException(status_code=404, detail="User location not found")
        return mapLocationTableToLocation(location)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
@sensitiveRateLimit()
async def createLocation(
    countryName: str,
    locationManager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Create a new location.
    """
    try:
        await locationManager.createLocation(countryName)
        return {"message": "Location created successfully"}
    except LocationManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{locationId}/update")
@sensitiveRateLimit()
async def updateLocation(
    locationId: int,
    countryName: str,
    locationManager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Update an existing location.
    """
    try:
        await locationManager.updateLocation(locationId, countryName)
        return {"message": "Location updated successfully"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{locationId}")
@sensitiveRateLimit()
async def deleteLocation(
    locationId: int,
    locationManager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Delete a location.
    """
    try:
        await locationManager.deleteLocation(locationId)
        return {"message": "Location deleted successfully"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationDeleteError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{locationId}", response_model=Location)
@apiRateLimit()
async def getLocation(
    locationId: int,
    locationManager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Get a location by ID.
    """
    try:
        return await locationManager.getLocation(locationId)
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

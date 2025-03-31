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

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
    responses={404: {"description": "Not found"}},
)


async def getLocationManager(
    dbSession: Annotated[AsyncSession, Depends(database.getDbSession)]
) -> LocationManager:
    return LocationManager(dbSession)


@router.post("/create", include_in_schema=False)
async def createLocation(
    countryName: str,
    manager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Create a new location.
    """
    try:
        await manager.createLocation(countryName)
        return {"message": "Location created successfully"}
    except LocationManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{locationId}/update", include_in_schema=False)
async def updateLocation(
    locationId: int,
    countryName: str,
    manager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Update an existing location.
    """
    try:
        await manager.updateLocation(locationId, countryName)
        return {"message": "Location updated successfully"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{locationId}", include_in_schema=False)
async def deleteLocation(
    locationId: int,
    manager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Delete a location.
    """
    try:
        await manager.deleteLocation(locationId)
        return {"message": "Location deleted successfully"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationDeleteError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{locationId}", response_model=Location)
async def getLocation(
    locationId: int,
    manager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Get a location by ID.
    """
    try:
        return await manager.getLocation(locationId)
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/all", response_model=List[Location])
async def getAllLocations(
    manager: Annotated[LocationManager, Depends(getLocationManager)],
):
    """
    Get all locations.
    """
    try:
        return await manager.getAllLocations()
    except LocationManagerException as e:
        raise HTTPException(status_code=400, detail=str(e)) 

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.location.LocationManager import LocationManager
from app.customExceptions import (
    LocationAlreadyExistsException,
    LocationDeleteError,
    LocationManagerException,
    LocationNotFoundException,
    LocationUpdateError,
)
from app.data import database

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
    responses={404: {"description": "Not found"}},
)


def getLocationManager(
    db: AsyncSession = Depends(database.getDbSession),
) -> LocationManager:
    return LocationManager(db)


@router.post("/create", include_in_schema=False)
async def createLocation(
    countryName: str,
    manager: Annotated[LocationManager, Depends(getLocationManager)]
) -> dict:
    """Hidden endpoint to create a new location."""
    try:
        location = await manager.createLocation(countryName)
        return {"message": f"Location '{location.country_name}' created successfully", "id": location.id}
    except LocationAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LocationManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{locationId}/update", include_in_schema=False)
async def updateLocation(
    locationId: int,
    newCountryName: str,
    manager: Annotated[LocationManager, Depends(getLocationManager)]
) -> dict:
    """Hidden endpoint to update a location."""
    try:
        location = await manager.updateLocation(locationId, newCountryName)
        return {"message": f"Location updated successfully to '{location.country_name}'"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{locationId}", include_in_schema=False)
async def deleteLocation(
    locationId: int,
    manager: Annotated[LocationManager, Depends(getLocationManager)]
) -> dict:
    """Hidden endpoint to delete a location."""
    try:
        await manager.deleteLocation(locationId)
        return {"message": f"Location with ID {locationId} deleted successfully"}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LocationDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{locationId}", include_in_schema=False)
async def getLocation(
    locationId: int,
    manager: Annotated[LocationManager, Depends(getLocationManager)]
) -> dict:
    """Hidden endpoint to get a location by ID."""
    try:
        location = await manager.getLocation(locationId)
        return {"id": location.id, "country_name": location.country_name}
    except LocationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) 

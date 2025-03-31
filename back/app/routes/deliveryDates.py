from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.delivery.DeliveryDateAssigner import DeliveryDateAssigner
from app.customExceptions import DeliveryDateAssignerException
from app.data import database

router = APIRouter(
    prefix="/delivery_dates",
    tags=["delivery_dates"],
    responses={404: {"description": "Not found"}},
)


def getDeliveryDateAssigner(
    db: AsyncSession = Depends(database.getDbSession),
) -> DeliveryDateAssigner:
    return DeliveryDateAssigner(db)


@router.post("/populate", include_in_schema=False)
async def populateDeliveryDates(
    assigner: Annotated[DeliveryDateAssigner, Depends(getDeliveryDateAssigner)]
) -> dict:
    """
    Hidden endpoint to populate the delivery dates table with random delivery days.
    This endpoint is not shown in the API schema.
    """
    try:
        await assigner.assignDeliveryDates()
        return {"message": "Successfully populated delivery dates"}
    except DeliveryDateAssignerException as e:
        raise HTTPException(status_code=500, detail=str(e)) 

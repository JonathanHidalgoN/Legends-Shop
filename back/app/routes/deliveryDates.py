from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.delivery.DeliveryDateAssigner import DeliveryDateAssigner
from app.customExceptions import DeliveryDateAssignerException
from app.data import database
from app.schemas.DeliveryDate import DeliveryDate

router = APIRouter()


def getDeliveryDateAssigner(
    db: AsyncSession = Depends(database.getDbSession),
) -> DeliveryDateAssigner:
    return DeliveryDateAssigner(db)


@router.get("/dates/{location_id}", response_model=List[DeliveryDate])
async def getDeliveryDates(
    request:Request,
    location_id: int,
    assigner: Annotated[DeliveryDateAssigner, Depends(getDeliveryDateAssigner)],
) -> List[DeliveryDate]:
    """
    Get delivery dates for a list of items based on location.
    """
    try:
        return await assigner.getItemDeliveryDates(location_id)
    except DeliveryDateAssignerException as e:
        raise HTTPException(status_code=500, detail=str(e))


#
#
# @router.post("/populate", include_in_schema=False)
# async def populateDeliveryDates(
#     assigner: Annotated[DeliveryDateAssigner, Depends(getDeliveryDateAssigner)],
# ) -> dict:
#     """
#     Hidden endpoint to populate the delivery dates table with random delivery days.
#     This endpoint is not shown in the API schema.
#     """
#     try:
#         await assigner.checkAndUpdateDeliveryDates()
#         return {"message": "Successfully populated delivery dates"}
#     except DeliveryDateAssignerException as e:
#         raise HTTPException(status_code=500, detail=str(e))

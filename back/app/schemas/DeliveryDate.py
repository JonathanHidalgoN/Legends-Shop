from pydantic import BaseModel
from datetime import date


class DeliveryDate(BaseModel):
    itemId: int
    locationId: int
    deliveryDate: date

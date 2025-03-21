from typing import List
from pydantic import BaseModel

from app.schemas.AuthSchemas import UserInDB
from app.schemas.Order import OrderSummary


class ProfileGoldResponse(BaseModel):
    userGold: int

class ProfileInfo (BaseModel):
    user: UserInDB
    ordersInfo: List[OrderSummary]

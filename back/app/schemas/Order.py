from datetime import datetime
from typing import List
from pydantic import BaseModel


class Order(BaseModel):
    id: int
    itemNames: List[str]
    userName: str
    total: int
    date: datetime


class OrderDataPerItem(BaseModel):
    itemId: int
    quantity: int
    total: int
    orderId: int

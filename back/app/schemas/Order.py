from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.Item import Item

class OrderItem(BaseModel):
    name:str
    cost:int

class Order(BaseModel):
    id: int
    items: List[OrderItem]
    userName: str
    total: int
    date: datetime

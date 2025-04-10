from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class Order(BaseModel):
    id: int
    itemNames: List[str]
    userName: str
    total: int
    orderDate: datetime
    deliveryDate: datetime
    status: OrderStatus


class OrderDataPerItem(BaseModel):
    itemId: int
    quantity: int
    total: int
    orderId: int

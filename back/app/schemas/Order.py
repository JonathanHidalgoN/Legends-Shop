from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"

class CarStatus(str, Enum):
    ADDED = "ADDED"
    DELETED = "DELETED"
    ORDERED = "ORDERED"


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


class OrderSummary(BaseModel):
    itemName: str
    basePrice: int
    timesOrdered: int
    totalSpend: int
    orderDates: List[datetime]

from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class CartStatus(str, Enum):
    ADDED = "ADDED"
    DELETED = "DELETED"
    ORDERED = "ORDERED"
    INCLIENT = "INCLIENT"


class CartItem(BaseModel):
    id: int | None
    itemId: int
    status: CartStatus


class Order(BaseModel):
    id: int
    itemNames: List[str]
    userName: str
    total: int
    orderDate: datetime
    deliveryDate: datetime
    status: OrderStatus
    location_id: int
    reviewed: bool = False


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

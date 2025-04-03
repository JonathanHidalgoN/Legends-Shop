from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.Order import OrderStatus
from app.data.models.OrderTable import OrderTable
from app.data.queries.orderQueries import (
    getOrdersWithStatusAndDeliveryDate,
    updateOrderStatus
)

class OrderStatusProcessor:
    def __init__(self, asyncSession: AsyncSession) -> None:
        self.asyncSession = asyncSession

    async def update_order_statuses(self) -> None:
        today: date = date.today()
        tomorrow: date = today.replace(day=today.day + 1)
        
        # Update PENDING to SHIPPED for orders with delivery date tomorrow
        pendingOrders: List[OrderTable] = await getOrdersWithStatusAndDeliveryDate(
            self.asyncSession,
            tomorrow,
            OrderStatus.PENDING
        )
        
        for order in pendingOrders:
            await updateOrderStatus(
                self.asyncSession,
                order.id,
                OrderStatus.SHIPPED
            )

        # Update SHIPPED to DELIVERED for orders with delivery date today
        shippedOrders: List[OrderTable] = await getOrdersWithStatusAndDeliveryDate(
            self.asyncSession,
            today,
            OrderStatus.SHIPPED
        )
        
        for order in shippedOrders:
            await updateOrderStatus(
                self.asyncSession,
                order.id,
                OrderStatus.DELIVERED
            ) 

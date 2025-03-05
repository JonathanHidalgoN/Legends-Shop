from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.customExceptions import OrderNotFoundException
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.schemas.Order import Order, OrderStatus


async def getOrderHistoryQuery(asyncSession: AsyncSession, userId: int) -> List[Order]:
    """"""
    result = await asyncSession.execute(
        select(
            OrderTable.id,
            OrderTable.total,
            OrderTable.order_date,
            OrderTable.delivery_date,
            OrderTable.status,
            ItemTable.name,
            UserTable.userName,
        )
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(UserTable, UserTable.id == userId)
        .where(OrderTable.user_id == userId)
    )
    rows = result.all()
    orders_dict = {}
    for (
        order_id,
        total,
        order_date,
        delivery_date,
        status,
        item_name,
        user_name,
    ) in rows:
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "id": order_id,
                "itemNames": [item_name],
                "userName": user_name,
                "total": total,
                "orderDate": order_date,
                "deliveryDate": delivery_date,
                "status": status,
            }
        else:
            orders_dict[order_id]["itemNames"].append(item_name)
    return [Order(**order_data) for order_data in orders_dict.values()]

async def getOrderWithId(asyncSession: AsyncSession,orderId:int) -> None:
    result = await asyncSession.execute(select(OrderTable)
                                        .where(OrderTable.id == orderId))
    return result.scalars().first()

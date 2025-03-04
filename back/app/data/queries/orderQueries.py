from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable 
from app.schemas.Order import Order


async def getOrderHistoryQuery(asyncSession: AsyncSession, userId: int)->List[Order]:
    """"""
    result = await asyncSession.execute(
        select(
            OrderTable.id,
            OrderTable.total,
            OrderTable.order_date,
            ItemTable.name,
            UserTable.userName
        )
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(UserTable, UserTable.id == userId)
        .where(OrderTable.user_id == userId)
    )
    rows = result.all()
    orders_dict = {}
    for order_id, total, order_date, item_name, user_name in rows:
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "id": order_id,
                "itemNames": [item_name],
                "userName": user_name,
                "total": total,
                "date": order_date
            }
        else:
            orders_dict[order_id]["itemNames"].append(item_name)
    return [Order(**order_data) for order_data in orders_dict.values()]


from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.customExceptions import OrderNotFoundException
from app.data.models.UserTable import UserTable
from app.data.models.ItemTable import ItemTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.schemas.Order import Order, OrderStatus


async def getOrderHistoryQuery(asyncSession: AsyncSession, userId: int,
    orderStatus: str = "ALL",
    minOrderDate: Optional[date] = None,
    maxOrderDate: Optional[date] = None,
    minDeliveryDate: Optional[date] = None,
    maxDeliveryDate: Optional[date] = None,
    sortField: Optional[str] = None,
    sortOrder: Optional[str] = None,
    filterItemNames: Optional[List[str]] = None 

                               ) -> List[Order]:
    """"""
    query = (
        select(
            OrderTable.id,
            OrderTable.total,
            OrderTable.order_date,
            OrderTable.delivery_date,
            OrderTable.status,
            ItemTable.name,
            UserTable.userName,
            OrderItemAssociation.c.quantity,
        )
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(UserTable, UserTable.id == userId)
        .where(OrderTable.user_id == userId)
    )

    filters = []
    
    if orderStatus != "ALL":
        filters.append(OrderTable.status == orderStatus)
    if minOrderDate:
        filters.append(OrderTable.order_date >= minOrderDate)
    if maxOrderDate:
        filters.append(OrderTable.order_date <= maxOrderDate)
    if minDeliveryDate:
        filters.append(OrderTable.delivery_date >= minDeliveryDate)
    if maxDeliveryDate:
        filters.append(OrderTable.delivery_date <= maxDeliveryDate)
    if filterItemNames:
        filters.append(ItemTable.name.in_(filterItemNames))

    if filters:
        query = query.where(*filters)

    if sortField:
        if sortField == "price":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.total.desc())
            else:
                query = query.order_by(OrderTable.total.asc())
        elif sortField == "orderDate":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.order_date.desc())
            else:
                query = query.order_by(OrderTable.order_date.asc())
        elif sortField == "deliveryDate":
            if sortOrder == "desc":
                query = query.order_by(OrderTable.delivery_date.desc())
            else:
                query = query.order_by(OrderTable.delivery_date.asc())
        elif sortField == "quantity":
            if sortOrder == "desc":
                query = query.order_by(OrderItemAssociation.c.quantity.desc())
            else:
                query = query.order_by(OrderItemAssociation.c.quantity.asc())

    result = await asyncSession.execute(query)

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
        quantity
    ) in rows:
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "id": order_id,
                "itemNames": [item_name for _ in range(quantity)],
                "userName": user_name,
                "total": total,
                "orderDate": order_date,
                "deliveryDate": delivery_date,
                "status": status,
            }
        else:
            orders_dict[order_id]["itemNames"].append(item_name)
    return [Order(**order_data) for order_data in orders_dict.values()]


async def getOrderWithId(asyncSession: AsyncSession, orderId: int) -> None:
    result = await asyncSession.execute(
        select(OrderTable).where(OrderTable.id == orderId)
    )
    return result.scalars().first()

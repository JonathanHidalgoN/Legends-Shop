from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.UserTable import UserTable
from app.data.models.GoldTable import GoldTable 
from app.data.models.ItemTable import ItemTable
from app.data.models.OrderTable import OrderItemAssociation, OrderTable
from app.schemas.Order import Order, OrderSummary


async def getOrderHistoryByUserId(
    asyncSession: AsyncSession,
    userId: int,
) -> List[Order]:
    """
    """
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
        .select_from(OrderTable)
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(UserTable, UserTable.id == OrderTable.user_id)
        .where(OrderTable.user_id == userId)
    ).order_by(OrderTable.order_date.desc())

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
        quantity,
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
    """
    Retrieve a single order record by its ID.

    This asynchronous function executes a database query using the provided
    asynchronous session to fetch an order record from the OrderTable that
    matches the specified orderId. It returns the first matching order record,
    or None if no such record exists.

    Args:
        asyncSession (AsyncSession): The asynchronous SQLAlchemy session to execute the query.
        orderId (int): The unique identifier of the order to be retrieved.

    Returns:
        Optional[OrderTable]: The first OrderTable record that matches the orderId,
        or None if no record is found.
    """
    result = await asyncSession.execute(
        select(OrderTable).where(OrderTable.id == orderId)
    )
    return result.scalars().first()


async def getUniqueItemNamesQuantityAndBasePriceByUserName(
    asyncSession: AsyncSession, userName: str
) -> List[OrderSummary]:
    query = (
        select(
            ItemTable.name,
            GoldTable.base_cost,
            func.sum(OrderItemAssociation.c.quantity).label("total_quantity"),
        )
        .select_from(UserTable)
        .join(OrderTable, OrderTable.user_id == UserTable.id)
        .join(OrderItemAssociation, OrderTable.id == OrderItemAssociation.c.order_id)
        .join(ItemTable, OrderItemAssociation.c.item_id == ItemTable.id)
        .join(GoldTable, GoldTable.id == ItemTable.id)
        .where(UserTable.userName == userName)
        .group_by(ItemTable.name,GoldTable.base_cost)
        .order_by(ItemTable.name)
    )

    result = await asyncSession.execute(query)
    rows = result.all()
    finalList = []

    for (
        name,
        baseCost,
        totalQuantity,
    ) in rows:
        ordSummary = OrderSummary(itemName=name,
                                                 basePrice=baseCost,
                                                 timesOrdered=totalQuantity,
                                                 totalSpend=int(baseCost*totalQuantity),
                                                 orderDates=[])
        finalList.append(ordSummary)

    return finalList

